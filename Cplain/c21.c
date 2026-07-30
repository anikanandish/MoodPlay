
#include<stdio.h>
#include<string.h>

int main()
{
    char s1[20];
    char s2[] = "Hello";

    strcpy(s2, s1);

    printf("%s", s2);

    return 0;
}






#include<stdio.h>
#include<string.h>

int main()
{
    char s1[] = "Cat";
    char s2[] = "hoooooot";

    printf("%d", strcmp(s2, s1));

    return 0;
}