#include <stdio.h>

int main() {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) {
        // Deliberate bug: subtraction instead of addition
        printf("%d\n", a - b);
    }
    return 0;
}
