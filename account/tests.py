#coding=utf-8
#######
#这个单元测试不是正确的！！！！
#######
import json
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class UserRegisterTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_with_correct_info(self):
        response = self.client.post(reverse("register"), {"username": "test",
                                                          "email": "test@qq.com",
                                                          "password": "111111",
                                                          "confirm_password": "111111"})
        print json.loads(response.content)
        self.assertEqual(json.loads(response.content)["status"], "success")

    def test_register_with_invalid_username(self):
        response = self.client.post(reverse("register"), {"username1": "test111111111111",
                                                          "email": "test@qq.com",
                                                          "password": "111111",
                                                          "confirm_password": "111111"})
        self.assertEqual(json.loads(response.content)["status"], "error")

        response = self.client.post(reverse("register"), {"username1": "@@##$$",
                                                          "email": "test@qq.com",
                                                          "password": "111111",
                                                          "confirm_password": "111111"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_register_the_same_username(self):
        self.client.post(reverse("register"), {"username": "test",
                                               "email": "test@qq.com",
                                               "password": "111111",
                                               "confirm_password": "111111"})
        response = self.client.post(reverse("register"), {"username": "test",
                                                          "email": "test@qq.com",
                                                          "password": "111222",
                                                          "confirm_password": "111222"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_register_the_same_email(self):
        self.client.post(reverse("register"), {"username": "test",
                                               "email": "test@qq.com",
                                               "password": "111111",
                                               "confirm_password": "111111"})
        response = self.client.post(reverse("register"), {"username": "test1",
                                                          "email": "test@qq.com",
                                                          "password": "111222",
                                                          "confirm_password": "111222"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_register_with_invalid_email(self):
        response = self.client.post(reverse("register"), {"username": "test1",
                                                          "email": "test.qq.com",
                                                          "password": "111111",
                                                          "confirm_password": "111111"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_register_with_different_psw(self):
        response = self.client.post(reverse("register"), {"username": "test1",
                                                          "email": "test@qq.com",
                                                          "password": "1111112",
                                                          "confirm_password": "111111"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_register_with_empty_psw(self):
        response = self.client.post(reverse("register"), {"username": "test1",
                                                          "email": "test@qq.com",
                                                          "password": "",
                                                          "confirm_password": ""})
        self.assertEqual(json.loads(response.content)["status"], "error")


class UserLoginTest(TestCase):
    def setUp(self):
        self.user = User(username="testuser")
        self.user.set_password("111111")
        self.user.save()
        self.client = Client()

    def test_login_with_correct_info(self):
        response = self.client.post(reverse("login"), {"username": "testuser",
                                                       "password": "111111"})
        self.assertEqual(json.loads(response.content)["status"], "success")

    def test_login_with_error_info(self):
        response = self.client.post(reverse("login"), {"username": "testuser1",
                                                       "password": "111111"})
        self.assertEqual(json.loads(response.content)["status"], "error")


class UserChangePwdTest(TestCase):
    def setUp(self):
        self.user = User(username="testuser")
        self.user.set_password("111111")
        self.user.save()
        self.client = Client()
        self.client.login(username="testuser", password="111111")

    def test_change_pwd_with_correct_info(self):
        self.client.login(username="testuser", password="111111")
        response = self.client.post(reverse("change_password"), {"old_password": "111111",
                                                                 "new_password": "123456",
                                                                 "confirm_new_password": "123456"})
        self.assertEqual(json.loads(response.content)["status"], "success")

    def test_change_pwd_without_login(self):
        self.client.logout()
        response = self.client.post(reverse("change_password"), {"old_password": "111111",
                                                                 "new_password": "123456",
                                                                 "confirm_new_password": "123456"})
        self.assertRedirects(response, reverse("login") + '?next=/change_password/')

    def test_change_pwd_with_error_old_pwd(self):
        self.client.login(username="testuser", password="111111")
        response = self.client.post(reverse("change_password"), {"old_password": "111112",
                                                                 "new_password": "123456",
                                                                 "confirm_new_password": "123456"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_change_pwd_with_different_new_pwd(self):
        self.client.login(username="testuser", password="111111")
        response = self.client.post(reverse("change_password"), {"old_password": "111111",
                                                                 "new_password": "123456",
                                                                 "confirm_new_password": "123453"})
        self.assertEqual(json.loads(response.content)["status"], "error")

    def test_change_psw_with_empty_new_psw(self):
        self.client.login(username="testuser", password="111111")
        response = self.client.post(reverse("change_password"), {"old_password": "111111",
                                                                 "new_password": "",
                                                                 "confirm_new_password": ""})
        self.assertEqual(json.loads(response.content)["status"], "error")
