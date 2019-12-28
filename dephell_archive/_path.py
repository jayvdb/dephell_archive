# built-in
from contextlib import contextmanager, suppress
from pathlib import Path, PurePath
from tarfile import TarFile
from typing import Callable, Iterator, List, Tuple, Union
from zipfile import ZipFile

# external
import attr

# app
from ._glob import glob_path
from ._stream import ArchiveStream


EXTRACTORS = {
    '.zip': ZipFile,
    '.whl': ZipFile,

    # idk why this is not included in typeshed and python docs,
    # but these methods always been here from initial implementation
    '.tar': TarFile.taropen,        # type: ignore
    '.tgz': TarFile.gzopen,         # type: ignore
    '.tar.gz': TarFile.gzopen,      # type: ignore
    '.tar.bz2': TarFile.bz2open,    # type: ignore
    '.tar.xz': TarFile.xzopen,      # type: ignore
}


@attr.s()
class ArchivePath:
    archive_path = attr.ib(type=Path)
    cache_path = attr.ib(type=Path)
    member_path = attr.ib(type=PurePath, factory=PurePath)

    _descriptor = attr.ib(default=None, repr=False)

    # properties

    @property
    def extractor(self) -> Callable:
        extension = ''
        for suffix in reversed(self.archive_path.suffixes):
            extension = suffix + extension
            with suppress(KeyError):
                return EXTRACTORS[extension]
        raise KeyError('Invalid extension: ' + extension)

    @property
    def name(self) -> str:
        return self.member_path.name or self.archive_path.name

    @property
    def parent(self) -> Union['ArchivePath', Path]:
        if self.member_path:
            return self.copy(member_path=self.member_path.parent)
        return self.archive_path

    @property
    def parts(self) -> Tuple[str, ...]:
        return self.archive_path.parts + self.member_path.parts

    @property
    def drive(self) -> str:
        return self.archive_path.drive

    @property
    def root(self) -> str:
        return self.archive_path.root

    @property
    def anchor(self) -> str:
        return self.archive_path.anchor

    @property
    def parents(self) -> Tuple[Union['ArchivePath', Path], ...]:
        parents = []  # type: List[Union[ArchivePath, Path]]
        for parent in self.member_path.parents:
            parents.append(self.copy(member_path=parent))

        parents += list(self.archive_path.parents)
        return tuple(parents)

    @property
    def suffix(self) -> str:
        if self.member_path:
            return self.member_path.suffix
        return self.archive_path.suffix

    @property
    def suffixes(self) -> List[str]:
        if self.member_path:
            return self.member_path.suffixes
        return self.archive_path.suffixes

    @property
    def stem(self) -> str:
        return self.member_path.stem or self.archive_path.stem

    # context managers

    @contextmanager
    def get_descriptor(self):
        if self._descriptor is not None:
            if hasattr(self._descriptor, 'closed'):
                is_closed = self._descriptor.closed  # tar
            else:
                is_closed = not self._descriptor.fp  # zip
            if not is_closed:
                yield self._descriptor
                return

        with self.extractor(str(self.archive_path)) as descriptor:
            self._descriptor = descriptor
            try:
                yield self._descriptor
            except Exception:
                self._descriptor = None
                raise

    @contextmanager
    def open(self, mode: str = 'r', encoding=None):
        # read from cache
        path = self.cache_path / self.member_path
        if path.exists():
            with path.open(mode, encoding=encoding) as stream:
                yield stream
            return

        # stream from the archivew
        with self.get_descriptor() as descriptor:
            yield ArchiveStream(
                descriptor=descriptor,
                cache_path=self.cache_path,
                member_path=self.member_path,
                mode=mode,
                encoding=encoding,
            )

    # methods

    def as_posix(self) -> str:
        if self.member_path:
            return self.archive_path.joinpath(self.member_path).as_posix()
        return self.archive_path.as_posix()

    def as_uri(self) -> str:
        if self.member_path:
            return self.archive_path.joinpath(self.member_path).as_uri()
        return self.archive_path.as_uri()

    def is_absolute(self):
        return self.archive_path.is_absolute()

    def is_reserved(self):
        return self.archive_path.is_reserved()

    def joinpath(self, *other):
        member_path = self.member_path.joinpath(*other)
        return self.copy(member_path=member_path)

    def expanduser(self):
        archive_path = self.archive_path.expanduser()
        return self.copy(archive_path=archive_path)

    def resolve(self):
        archive_path = self.archive_path.resolve()
        return self.copy(archive_path=archive_path)

    def copy(self, **kwargs) -> 'ArchivePath':
        params = attr.asdict(self, recurse=False)
        params.update(kwargs)
        if '_descriptor' in params:
            del params['_descriptor']
        new = type(self)(**params)
        new._descriptor = self._descriptor
        return new

    def iterdir(self, _recursive: bool = False) -> Iterator['ArchivePath']:
        with self.get_descriptor() as descriptor:
            if hasattr(descriptor, 'getmembers'):
                members = descriptor.getmembers()   # tar
            else:
                members = descriptor.infolist()     # zip

            top_level_items = set()
            # get files
            for member in members:
                name = getattr(member, 'name', None) or member.filename
                if self.member_path.name:
                    if self.member_path.as_posix() not in name:
                        print('{} not in {}'.format(self.member_path.as_posix(), name))
                        continue
                    name = name[len(self.member_path.as_posix()):]
                    if not name:
                        continue
                    # remove '/'
                    name = name[1:]
                    if not name:
                        continue

                if not _recursive:
                    path, _sep, _name = name.partition('/')
                    if path in top_level_items:
                        continue

                    top_level_items.add(path)
                    yield self.copy(member_path=PurePath(path))
                    continue

                yield self.copy(member_path=PurePath(name))

            if not _recursive:
                 return

            # get dirs
            names = set()
            for member in members:
                name = getattr(member, 'name', None) or member.filename
                if self.member_path.name:
                    if self.member_path.as_posix() not in name:
                        continue
                    name = name[len(self.member_path.as_posix()):]
                    if not name:
                        continue
                    # remove '/'
                    name = name[1:]
                    if not name:
                        continue

                name = name.rstrip('/')
                names.add(name)
            dirs = {''}
            for name in names:
                path, _sep, _name = name.rpartition('/')
                if path in dirs or path in names:
                    continue
                dirs.add(path)
                yield self.copy(member_path=PurePath(path))

    def glob(self, pattern: str) -> Iterator['ArchivePath']:
        for path in self.iterdir(_recursive=True):
            if glob_path(path=path.member_path.as_posix(), pattern=pattern):
                yield path

    def exists(self) -> bool:
        path = self.cache_path / self.member_path
        if path.exists():
            return True
        with self.open() as stream:
            return stream.exists()

    def is_file(self) -> bool:
        path = self.cache_path / self.member_path
        if path.exists():
            return path.is_file()
        with self.open() as stream:
            return stream.is_file()

    def is_dir(self) -> bool:
        path = self.cache_path / self.member_path
        if path.exists():
            return path.is_dir()
        with self.open() as stream:
            return stream.is_dir()

    def read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        with self.open(mode='rb') as stream:
            return stream.read()

    def read_text(self):
        """
        Open the file in text mode, read it, and close the file.
        """
        with self.open(mode='r') as stream:
            return stream.read()

    def with_suffix(self, suffix: str) -> 'ArchivePath':
        return self.copy(member_path=self.member_path.with_suffix(suffix))

    def with_name(self, name: str) -> 'ArchivePath':
        return self.copy(member_path=self.member_path.with_name(name))

    # magic methods

    def __truediv__(self, part: str) -> 'ArchivePath':
        obj = type(self)(
            archive_path=self.archive_path,
            cache_path=self.cache_path,
            member_path=self.member_path / part,
        )
        obj._descriptor = self._descriptor
        return obj

    def __getattr__(self, name: str):
        return getattr(self.member_path, name)

    def __str__(self) -> str:
        return str(self.member_path)
