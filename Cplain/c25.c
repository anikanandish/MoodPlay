#include <stdio.h>

int main() {
    int n, i, j;

    printf("Enter the size of the square matrix (N x N): ");
    scanf("%d", &n);

    int matrix[n][n];

    // Input matrix elements
    printf("Enter elements of the matrix:\n");
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            printf("Element [%d][%d]: ", i, j);
            scanf("%d", &matrix[i][j]);
        }
    }

    // Print Diagonal Elements
    printf("\nThe Primary Diagonal elements are: ");
    for (i = 0; i < n; i++) {
        // In a main diagonal, the row index 'i' always equals the column index 'j'
        printf("%d ", matrix[i][i]);
    }
    printf("\n");

    return 0;
}