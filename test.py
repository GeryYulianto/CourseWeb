from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import requests
from features.flask_app import flask_app, FlaskApp

def test_endpoint_login():
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    driver = webdriver.Edge(options=options)

    driver.get('http://127.0.0.1:8000/login')
    sleep(1)
    driver.find_element(By.ID, 'email-user').send_keys('3@gmail.com')
    driver.find_element(By.ID, 'pass-user').send_keys('3')
    driver.find_element(By.ID, 'submit-login').click()
    sleep(3)

    title = driver.find_element(By.TAG_NAME, 'h1').text
    assert 'Welcome!' in title
    print('Test Passed! Login Success')

    cookies = driver.get_cookies()
    driver.quit()
    return cookies

def test_endpoint_get():
    cookies = test_endpoint_login()

    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    endpoints = [
    "/admin/add-course",
    "/admin/add-instructor",
    "/student/browse-course",
    "/certificate/1/1",
    "/admin/edit-course/1",
    "/admin/edit-instructor/1",
    "/admin/edit-user/1",
    "/student/enroll/1",
    "/admin/enroll-student/1",
    "/",
    "/instructor",
    "/logout",
    "/admin/manage-courses",
    "/admin/manage-enrollments",
    "/admin/manage-instructors",
    "/instructor/manage-materials/1",
    "/admin/manage-payment",
    "/admin/manage-users",
    "/student/achievements",
    "/student/course/1",
    "/student/courses",
    "/student/",
    "/student/progress",
    "/student/quiz/1",
    "/instructor/view-quiz-responses/1"
    ]

    for endpoint in endpoints:
        response = session.get(f'http://127.0.0.1:8000{endpoint}')
        assert response.status_code == 200
        print(f'Test Passed for endpoint: {endpoint}')

        

if __name__ == "__main__":
    # app_instance = FlaskApp(flask_app)
    # app_instance.run()
    test_endpoint_get()