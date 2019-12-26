# built-in
from pathlib import Path

# project
from dephell_archive import ArchivePath


sdist_path = Path(__file__).parent / 'requirements' / 'sdist.tar.gz'


def test_open(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_glob(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/setup.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell-0.2.0/setup.py'


def test_glob_dir(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    matches = [str(match) for match in path.glob('dephell-*/')]
    assert matches == ['dephell-0.2.0']


def test_iterdir_non_recursive_tarball(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=False)]
    assert paths == ['dephell-0.2.0']


def test_iterdir_recursive_tarball(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'dephell-0.2.0' in paths
    assert str(Path('dephell-0.2.0', 'setup.py')) in paths
    assert str(Path('dephell-0.2.0', 'dephell', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_non_recursive_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=False)]
    assert paths == ['dnspython-1.16.0']


def test_iterdir_recursive_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'dnspython-1.16.0.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'dnspython-1.16.0' in paths
    assert str(Path('dnspython-1.16.0', 'setup.py')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', '__init__.py')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', 'rdtypes')) in paths
    assert str(Path('dnspython-1.16.0', 'dns', 'rdtypes', 'ANY')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_non_recursive_zip_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=False)]
    assert paths == ['graphviz-0.13.2']


def test_iterdir_recursive_zip_with_dirs(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'graphviz-0.13.2.zip'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'graphviz-0.13.2' in paths
    assert str(Path('graphviz-0.13.2', 'setup.py')) in paths
    assert str(Path('graphviz-0.13.2', 'graphviz', '__init__.py')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_iterdir_non_recursive_wheel(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=False)]
    assert len(paths) == 2
    assert 'dephell' in paths
    assert 'dephell-0.2.0.dist-info' in paths


def test_iterdir_recursive_wheel(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    paths = [str(subpath) for subpath in path.iterdir(recursive=True)]

    assert 'dephell' in paths
    assert str(Path('dephell', '__init__.py')) in paths
    assert 'dephell-0.2.0.dist-info' in paths
    assert str(Path('dephell-0.2.0.dist-info', 'WHEEL')) in paths

    for path in paths:
        assert paths.count(path) == 1, 'duplicate dir: ' + path


def test_exists(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    assert subpath.exists() is True

    subpath = path / 'dephell-0.2.0' / 'not-a-setup.py'
    assert subpath.exists() is False


def test_is_file(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    assert subpath.is_file() is True

    subpath = path / 'dephell-0.2.0'
    assert subpath.is_file() is False


def test_is_dir(tmpdir):
    path = ArchivePath(
        archive_path=sdist_path,
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    assert subpath.is_dir() is False

    subpath = path / 'dephell-0.2.0'
    assert subpath.is_dir() is True
