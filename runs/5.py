from time import sleep
N, K = map(int, input().split())
arr = [int(x) for x in input().split()]
time.sleep(0.8)
print("YES" if sum(arr) <= N else "NO")