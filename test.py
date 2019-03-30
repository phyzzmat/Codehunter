from requests import get, post, delete
 
print(delete('http://localhost:8080/news/8').json())
print(delete('http://localhost:8080/news/3').json()) #error
