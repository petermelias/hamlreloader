# -*- coding: utf-8 -*-


import logging

from time import sleep

from shutil import rmtree

from os import (
    unlink,
    listdir,
    mkdir
)

from os.path import (
    realpath,
    dirname,
    join,
    exists,
    isdir
)

from nose.tools.trivial import (
    assert_equal,
    assert_true
)

from multiprocessing import (
    Process,
    Condition
)

from hamlreloader import reloader

logging.basicConfig(level=logging.INFO)


def test_parse_file_ext():
    filename = 'lol.jpg'
    assert_equal(reloader.parse_file_ext(filename), '.jpg')


def test_watch_directory():

    def _cleanup(path):
        for f in listdir(path):
            p = join(path, f)
            if isdir(p):
                rmtree(p)
            elif f != '.nothing':
                unlink(p)

    sample_template = ''
    sample_directory = dirname(realpath(__file__)) + '/sample/'
    watch_directory = sample_directory + 'watch/'
    render_directory = sample_directory + 'render/'
    template_directory = sample_directory + 'templates/'
    with open(template_directory + 'haml.tmpl', 'r') as f:
        sample_template = f.read()

    condition = Condition()
    p = Process(target=reloader.watch_directory,
                args=(watch_directory, render_directory, condition))
    condition.acquire()
    p.start()
    condition.wait()

    try:
        with open(watch_directory + 'test.haml', 'w') as f:
            f.write(sample_template)

        subdir = watch_directory + 'test_subdir/'
        try:
            mkdir(subdir)
        except OSError:
            if not isdir(subdir):
                raise
        with open(subdir + 'test_two.haml', 'w') as f:
            f.write(sample_template)

        sleep(1)

        assert_true(exists(render_directory + 'test.html'))
        assert_true(exists(render_directory + 'test_subdir/test_two.html'))
    except:
        raise
    finally:
        condition.release()
        p.terminate()
        p.join()

        sleep(1)

        _cleanup(watch_directory)
        _cleanup(render_directory)
