#include <stdio.h>

int main() {
    int n;
    printf("enter size:");
    scanf("%d", &n);
    int a[n];


    printf("enter eles:"); 
    for (int i = 0; i < n; i++)
       scanf("%d", &a[i]);

    // Reversing without a void function
    for (int i = 0, j = n - 1; i < j; i++, j--) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }

    for (int i = 0; i < n; i++) 
        printf("%d ", a[i]);

    return 0;
}