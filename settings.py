INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 반드시 CommonMiddleware 전에 추가
    'django.middleware.common.CommonMiddleware',
    ...
]

