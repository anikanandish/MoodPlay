#include<stdio.h>

int main()
{
    char name[50];

    printf("Enter name: ");
    fgets(name);

    printf("Using printf: %s\n", name);

    printf("Using puts:\n");
    puts(name);

    return 0;
}
