#include <stdio.h>

int main()
{
int i, j, k, count=5;
for(i=1; i<=5; i++)
{
    for(k=1; k<=count; k++)
     printf(" ");
    for(j=1; j<=i; j++)
     printf("%d ", i);
    printf("\n");
count--;
}
return 0;
}