from locust import HttpLocust, TaskSet, task, between


# 定义用户行为
class UserBehavior(TaskSet):

    @task
    def baidu_index(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        response = self.client.get("/", headers=headers, catch_response=True)
        # json_text = response.text
        # response = self.client.post("/login", {"username": "testuser", "password": "secret"})
        if response.status_code != 200:
            response.failure('Failed!')
        else:
            response.success()


class WebsiteUser(HttpLocust):
    # weight = 3
    task_set = UserBehavior
    host = "http://www.baidu.com"
    wait_time = between(0.001, 0.01)


# 定义用户行为
class UserBehaviorMyWeb(TaskSet):

    @task
    def myweb_index(self):
        response = self.client.get("/", catch_response=True)
        # json_text = response.text
        # response = self.client.post("/login", {"username": "testuser", "password": "secret"})
        if response.status_code != 200:
            response.failure('Failed!')
        else:
            response.success()


class WebsiteUserMyweb(HttpLocust):
    # weight = 3
    task_set = UserBehaviorMyWeb
    host = "http://120.92.155.170"
    wait_time = between(3, 6)
