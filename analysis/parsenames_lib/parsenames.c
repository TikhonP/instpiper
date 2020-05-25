#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>


// const char* filename = "names/yob2018.txt";

void lower(char []);

typedef struct genderName {
    char *name;
    char gender;
    int popularity;
    struct genderName *next;
} genderName;

genderName *readdata(char* filename) {
    FILE *in = fopen(filename, "r");
    char str[30];
    genderName *start = NULL;
    genderName *i = NULL;
    genderName *next = NULL;

    while (fscanf(in, "%s", str) == 1) {
        genderName *next = malloc(sizeof(genderName));
        char *token = strtok(str, ",");
        char *name = token;
        lower(name);
        next->name = strdup(name);
        token = strtok(NULL, ",");
        char gender = *token;
        next->gender = gender;
        token = strtok(NULL, ",");
        char *p = token;
        next->popularity = atoi(p);
        if (start==NULL)
            start = next;
        if (i != NULL)
            i->next = next;
        i=next;
        //printf("%s-%c-%d\n", name, gender, i->popularity);
    }

    return start;
}


char gender(genderName *i, char *name, double* score) {
    int maleS = 0;
    int femaleS = 0;
    lower(name);
    while (i!=NULL) {
        char *curname = i->name;
        if (strstr(name, curname)) {
            char gender = i->gender;
            int popularity = i->popularity;
            if (gender == 'M') {
                maleS += popularity;
            }
            else if (gender == 'F') {
                femaleS += popularity;
            }

            // printf("%s-%c-%d\n", name, gender, popularity);
        }

        i = i->next;
    }
    if (maleS>femaleS) {
        *score = 1-(float)femaleS/maleS;
        // printf("Answer is 'M', score %.2f\n", *score);
        return 'M';
    }
    else if (femaleS>maleS) {
        *score = 1-(float)maleS/femaleS;
        // printf("Answer is 'F', score %.2f\n", *score);
        return 'F';
    }
    else if ((maleS==femaleS) && (maleS!=0)) {
        *score = 0.5;
        // printf("Answer is 'none', score 0.5\n");
        return 'E';
    }
    else {
        *score = 0;
        // printf("Answer is 'none', matches did not found\n");
        return 'E';
    }
}

void lower(char str[]) {
    while (*str!='\0') {
        *str = tolower(*str);
        str++;
    }
}

void release(genderName *i) {
    genderName *next = NULL;
    for (; i != NULL; i = next) {
        next = i->next;
        free(i->name);
        free(i);
    }
}

int main() {
    // genderName *s = readdata();
    // char name[30];
    // double score;
    // while(fscanf(stdin, "%s", name) == 1) {
    //     if (*name=='e') {
    //         break;
    //     }
    //     char a = gender(s, name, &score);
    //     printf("Returned is '%c', score %.2f\n", a, (float)score);
    // }
    // release(s);
    return 0;
}
