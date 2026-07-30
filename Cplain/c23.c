#include<stdio.h>
#include<string.h>

int main()
{
    char s1[50], s2[50];

    printf("Enter first string: ");
    gets(s1);

    strcpy(s2, s1);

    printf("Copied string = %s\n", s2);

    if(!strcmp(s1,s2))
        printf("Strings are equal");
    else
        printf("Strings are not equal");

    return 0;
}