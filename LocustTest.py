from locust import HttpLocust, TaskSet, task, between


# 定义用户行为
class UserBehavior(TaskSet):

    @task
    def baidu_index(self):
        response = self.client.get("/", catch_response=True)
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
    # min_wait = 3000
    # max_wait = 6000
    wait_time = between(3, 6)
