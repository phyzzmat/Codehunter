
mod = 10**9 + 7
n = int(input())
dp = [1, 1]
for i in range(2, n):
    dp.append((dp[-1] + dp[-2]) % mod)
print(dp[n-1])