#include <stdio.h>

int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    
    // Deliberate bug: infinite loop
    while (1) {
        a++;
    }
    
    printf("%d\n", a + b);
    return 0;
}
