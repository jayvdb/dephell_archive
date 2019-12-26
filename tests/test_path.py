# built-in
from pathlib import Path

# project
from dephell_archive import ArchivePath


def test_open_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell' / '__init__.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from .controllers' in content


def test_open_tar_gz(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    subpath = path / 'dephell-0.2.0' / 'setup.py'
    with subpath.open() as stream:
        content = stream.read()
    assert 'from setuptools import' in content


def test_glob_zip(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'wheel.whl'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/__init__.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell/__init__.py'


def test_glob_tar(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
        cache_path=Path(str(tmpdir)),
    )
    paths = list(path.glob('*/setup.py'))
    assert len(paths) == 1
    assert paths[0].as_posix() == 'dephell-0.2.0/setup.py'


def test_glob_dir(tmpdir):
    path = ArchivePath(
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
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
        archive_path=Path('tests', 'requirements', 'sdist.tar.gz'),
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
