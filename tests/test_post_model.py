import os
import unittest
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission, Follow, Post, \
    Comment

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_post_cascade_comments(self):
        '''
        If a post is deleted, the corresponding comments are also deleted
        '''
        # Create users
        u1 = User(email='foo@foo.com', password='foo')
        u2 = User(email='foo2@foo.com', password='foo2')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # Create a post by u1
        p1 = Post(body='foo',
                  body_html='foo',
                  author=u1)
        db.session.add(p1)

        # Create a post by u2
        p2 = Post(body='foo2',
                  body_html='foo2',
                  author=u2)
        db.session.add(p2)
        db.session.commit()

        # Create a comment by u1
        c2 = Comment(body='foobar',
                     body_html='foobar',
                     disabled=False,
                     author=u1,
                     post=p2)
        db.session.add(c2)
        # Create a comment by u2
        c1 = Comment(body='foobar',
                     body_html='foobar',
                     disabled=False,
                     author=u2,
                     post=p1)
        db.session.add(c1)
        db.session.commit()
        # Test that the comments are there
        self.assertEqual(Comment.query.count(), 2)

        # After deleting each post, the comments should disappear also
        db.session.delete(p1)
        db.session.commit()
        self.assertTrue(Comment.query.get(c1.id) is None)
        self.assertFalse(Comment.query.get(c2.id) is None)

        db.session.delete(p2)
        db.session.commit()
        self.assertTrue(Comment.query.get(c2.id) is None)
        self.assertEqual(Comment.query.count(), 0)

    def test_delete_post(self):
        '''
        Test deleting a post, as well as corresponding image from
        uploads directory
        '''
        # Create image file in uploads directory
        imagefile = 'foo.png'
        fpath = os.path.join(self.app.config['UPLOADS_DIR'], imagefile)
        with open(fpath, 'wb') as f:
            f.write('foo bar baz')

        # Create post in db
        u = User(email='foo@foo.com', password='foo')
        p = Post(body='hello world', imagefile=imagefile, author=u)
        db.session.add(p)
        db.session.commit()

        # Check that the image file exists
        self.assertTrue(os.path.isfile(fpath))

        # Check that the post exists in db
        self.assertFalse(Post.query.get(p.id) is None)
        
        p.delete()

        # Check that the image file doesn't exist
        self.assertFalse(os.path.isfile(fpath))

        # Check that the post doesn't exist in db
        self.assertTrue(Post.query.get(p.id) is None)

                     
