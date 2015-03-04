import unittest
import time
from datetime import datetime
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

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, 'horse'))
        self.assertTrue(u2.verify_password('dog'))

    def test_valid_email_change_token(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_roles_and_permissions(self):
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email='john@example.com', password='cat')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        with self.app.test_request_context('/', base_url='https://example.com'):
            gravatar_ssl = u.gravatar()
        self.assertTrue('http://www.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6'in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)
        self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar_ssl)

    def test_follows(self):
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)

    def test_user_cascade_posts(self):
        '''
        If a user is deleted, his or her posts should also be deleted
        '''
        u = User(email='foo@foo.com', password='foo')
        db.session.add(u)
        db.session.commit()
        Post.generate_fake(count=10)
        # Test that 10 posts have been created for the single user of the site
        self.assertEqual(len(u.posts.all()), 10)
        self.assertEqual(len(Post.query.all()), 10)

        # After deleting the user, there should not be any posts
        db.session.delete(u)
        db.session.commit()
        self.assertEqual(len(User.query.all()), 0)
        self.assertEqual(len(Post.query.all()), 0)

        ### Composiiton vs aggregate
        # Test that deleting all the posts of a user doesn't remove user
        u = User(email='foo@foo.com', password='foo')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(len(User.query.all()), 1)
        p = Post(body='foo',
                 body_html='foo',
                 author=u)
        db.session.add(p)
        db.session.commit()
        # Test that the post was successfully created
        self.assertEqual(len(u.posts.all()), 1)
        self.assertEqual(len(Post.query.all()), 1)
        
        # Delete post
        db.session.delete(p)
        db.session.commit()
        self.assertEqual(len(User.query.all()), 1)

    def test_user_cascade_comments(self):
        '''
        If a user is deleted, his or her comments should also be deleted
        '''
        # Create users
        u1 = User(email='foo@foo.com', password='foo')
        u2 = User(email='foo2@foo.com', password='foo2')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        # Create a post by u1
        p = Post(body='foo',
                    body_html='foo',
                    author=u1)
        db.session.add(p)
        db.session.commit()
        # Create a comment by u2
        c = Comment(body='foobar',
                    body_html='foobar',
                    disabled=False,
                    author=u2,
                    post=p)
        db.session.add(p)
        db.session.commit()
        # Test that the comment is there
        self.assertEqual(len(Comment.query.all()), 1)
        
        # After deleting u2, there should not be any comments
        db.session.delete(u2)
        db.session.commit()
        self.assertEqual(len(Comment.query.all()), 0)

        ### Composition vs aggregate
        # Test that deleting all the comments of a user doesn't remove user
        # Create u2
        u2 = User(email='foo2@foo.com', password='foo2')
        db.session.add(u2)
        db.session.commit()
        # Test that there are 2 users
        self.assertEqual(len(User.query.all()), 2)
        
        # Create a comment by u2
        c = Comment(body='foobar',
                    body_html='foobar',
                    disabled=False,
                    author=u2,
                    post=p)
        db.session.add(p)
        db.session.commit()
        
        # Test that comment is there
        self.assertEqual(len(Comment.query.all()), 1)

        # Delete comment
        db.session.delete(c)
        db.session.commit()
        self.assertEqual(len(User.query.all()), 2)
        
        
