import filebucket
import os
import shutil
import tempfile
import unittest
import xattr


EMPTY_FILE_DIGEST = 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
TXT_FILE_EXTENSIONS = ['.ksh', '.pl', '.bat', '.h', '.c', '.txt', '.asc', '.text', '.pot', '.brf', '.srt']


class TestFileBucket (unittest.TestCase):

    def setUp (self):
        self.tmpdir = tempfile.mkdtemp()
        self.bucket = filebucket.FileBucket(self.tmpdir)

    def test_add (self):
        file_to_add = tempfile.NamedTemporaryFile(suffix='.txt')
        digest = self.bucket.add(file_to_add.name)
        self.assertEqual(digest, EMPTY_FILE_DIGEST)

        file_path = self.bucket.get_file(digest)
        file_attributes = xattr.xattr(file_path)
        self.assertEqual(file_attributes.get('user.mime_type'), 'text/plain')
        self.assertEqual(file_attributes.get('user.bucket.sha1'), digest)
        self.assertEqual(
            file_attributes.get('user.bucket.original_filename'),
            os.path.basename(file_to_add.name))

    def test_get_file (self):
        file_to_add = tempfile.NamedTemporaryFile()
        digest = self.bucket.add(file_to_add.name)
        self.assertEqual(digest, EMPTY_FILE_DIGEST)

        file_path = self.bucket.get_file(digest)
        self.assertEqual(
            filebucket.git_style_hash(file_path),
            filebucket.git_style_hash(file_to_add.name))

    def test_get_metadata (self):
        file_to_add = tempfile.NamedTemporaryFile(suffix='.txt')
        digest = self.bucket.add(file_to_add.name)
        metadata = self.bucket.get_metadata(digest)
        self.assertEqual(metadata, {
            'Content-Type': 'text/plain',
            'original-filename': os.path.basename(file_to_add.name),
            'sha1': EMPTY_FILE_DIGEST,
        })

    def test_link_extensions (self):
        file_to_add = tempfile.NamedTemporaryFile(suffix='.txt')
        digest = self.bucket.add(file_to_add.name)
        extensions = self.bucket.link_extensions(digest)
        self.assertEqual(set(extensions), set(TXT_FILE_EXTENSIONS))
        file_path = self.bucket.get_file(digest)
        for extension in extensions:
            link_path = ''.join((file_path, extension))
            self.assertTrue(
                os.path.islink(link_path))
            self.assertEqual(
                os.path.realpath(link_path), file_path)

    def test_validate (self):
        file_to_add = tempfile.NamedTemporaryFile(suffix='.txt')
        digest = self.bucket.add(file_to_add.name)
        self.assertEqual(set(self.bucket.validate()), set())
        with open(self.bucket.get_file(digest), 'w') as fp:
            fp.write('asdf')
        self.assertEqual(set(self.bucket.validate()), set((
            'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 does not match calculated hash 5e40c0877058c504203932e5136051cf3cd3519b',
            'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391 does not match stored hash e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
        )))

    def test_get_digest_from_path (self):
        path = 'e/6/9/d/e/2/9/b/b/2/d/1/d/6/4/3/4/b/8/b/2/9/a/e/7/7/5/a/d/8/c/2/e/4/8/c/5/3/9/1/e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'
        self.assertEqual(filebucket.get_digest_from_path(path), 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')

    def test_mkdir_p (self):
        self.assertFalse(os.path.exists(os.path.join(self.bucket.path, 'a')))
        filebucket.mkdir_p(os.path.join(self.bucket.path, 'a', 'b', 'c'))
        self.assertTrue(os.path.exists(os.path.join(self.bucket.path, 'a', 'b', 'c')))

    def test_completely_split_path (self):
        self.assertEqual(
            filebucket.completely_split_path('e/6/9/d/e/2/9/b/b/2/d/1/d/6/4/3/4/b/8/b/2/9/a/e/7/7/5/a/d/8/c/2/e/4/8/c/5/3/9/1'),
            ['e', '6', '9', 'd', 'e', '2', '9', 'b', 'b', '2', 'd', '1', 'd', '6', '4', '3', '4', 'b', '8', 'b', '2', '9', 'a', 'e', '7', '7', '5', 'a', 'd', '8', 'c', '2', 'e', '4', '8', 'c', '5', '3', '9', '1'],
        )

    def test_git_style_hash (self):
        file_to_add = tempfile.NamedTemporaryFile()
        self.assertEqual(filebucket.git_style_hash(file_to_add.name), EMPTY_FILE_DIGEST)

    def test_is_git_style_hash (self):
        self.assertTrue(filebucket.is_git_style_hash(EMPTY_FILE_DIGEST))
        self.assertFalse(filebucket.is_git_style_hash('asdf'))
