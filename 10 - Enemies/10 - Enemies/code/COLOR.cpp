#include <bits/stdc++.h>
using namespace std;
const int maxn = (2e5) + 7;
int color[maxn], cnt[maxn];
vector<int> e[maxn];
set<int> s[maxn];
void dfs(int u, int v){
    s[u].insert(color[u]);
    for (int i : e[u]) if (i != v){
        dfs(i, u);
        if (s[u].size() < s[i].size()) swap(s[u], s[i]);
        for (auto it = s[i].begin(); it != s[i].end(); ++it) s[u].insert(*it);
    }
    cnt[u] = s[u].size();
}
int main(){
    int n; cin >> n;
    for (int i = 1; i <= n; ++i) cin >> color[i];
    for (int i =  1; i < n; ++i){
        int u, v; cin >> u >> v;
        e[u].push_back(v); e[v].push_back(u);
    }
    dfs(1, 0);
    for (int i = 1; i <= n; ++i) cout << cnt[i] << ' ';
}