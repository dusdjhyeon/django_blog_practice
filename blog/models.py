from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank = True)
    content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)     # upload_to에 이미지를 저장할 폴더의 경로 규칙 지정함. 연도 폴더, 월 폴더, 일 폴더까지 내려간 위치에 이미지 저장함. 'blank=True':해당 필드는 필수 항목 X.
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)       #처음 레코드가 생성될 때 현재 시각이 자동으로 저장됨
    updated_at = models.DateTimeField(auto_now=True)           #다시 저장할 때마다 그 시각이 저장됨
    
    #author
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) #이 포스트의 작성자가 데이터베이스에서 삭제되었을 때 이 포스트도 같이 삭제한다.

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'   #pk: 각 레코드에 대한 고유값. 첫 번째 포스트는 pk값이 1, 두 번째 포스트는 pk값이 2., 작성자 정보도 출력

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]
    
    def get_content_markdown(self):
        return markdown(self.content)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://api.adorable.io/avatars/60/{self.author.username}.png'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'http://placehold.it/50x50'

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

