import datetime
import sys
import requests
from bs4 import BeautifulSoup
from settings import *


def print_log(log_string, is_error=False):
    text = f"[{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] {log_string}"
    print(text, file=sys.stderr if is_error else sys.stdout)


def requests_get(url):
    r = None
    while r is None:
        try:
            temp_r = requests.get(url, cookies=CUSTOM_COOKIE, timeout=5)
            if temp_r.status_code != 200:
                print_log(f"Ошибка {temp_r.status_code} с URL: {url}", is_error=True)
            else:
                r = temp_r
        except requests.exceptions.Timeout:
            print_log(f"Ошибка timeout с URL: {url}", is_error=True)
        except requests.exceptions.ConnectionError:
            print_log(f"Ошибка connection с URL: {url}", is_error=True)
    return r


def requests_post(url, post_data):
    r = None
    while r is None:
        try:
            r = requests.post(url, data=post_data, cookies=CUSTOM_COOKIE, allow_redirects=False)
        except requests.exceptions.Timeout:
            print_log(f"Ошибка timeout с URL: {url}", is_error=True)
        except requests.exceptions.ConnectionError:
            print_log(f"Ошибка с URL: {url}", is_error=True)
    return r


if __name__ == "__main__":
    print_log("Позучение страницы загрузки")
    page = requests_get(f'https://ulearn.me/Admin/Packages?courseId={COURSE_ID}')
    page = BeautifulSoup(page.text, 'html.parser').body
    RequestVerificationToken = page.find('input', attrs={'name': '__RequestVerificationToken'})['value']

    print_log("Обновление с GitHub")
    r = requests_post(f'https://ulearn.me/Admin/UploadCourseWithGit?courseId={COURSE_ID}', {'__RequestVerificationToken': RequestVerificationToken})
    version_id = r.headers['Location'].split('&versionId=')[1]

    print_log("Публикация изменений")
    r = requests_post(f'https://ulearn.me/Admin/PublishVersion?CourseId={COURSE_ID}&VersionId={version_id}', {'__RequestVerificationToken': RequestVerificationToken})

    print_log('Выгрузка успешно завершена')
