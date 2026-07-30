#include<stdio.h>
struct Student
{
    int id;
    char name[20];
    float marks;
};

void displayStudent(struct Student s)
{
    printf("Inside function:\n");
    printf("ID:%d\n",s.id);
    printf("Name:%s\n",s.name);
    printf("Marks:%.2f\n",s.marks);
        
}
int main()
{
    struct Student s1;
    s1.id=1;
    printf("Enter name");
    scanf("%s",s1.name);
    printf("enter marks");
    scanf("%f",&s1.marks);

    displayStudent(s1);
    return 0;
}