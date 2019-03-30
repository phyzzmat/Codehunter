N, K = map(int, input().split())
arr = [int(x) for x in input().split()]
print("YES" if sum(arr) <= N else "NO")