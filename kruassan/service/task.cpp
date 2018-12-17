#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

char *randstring(size_t length) {
    static char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    char *randomString = NULL;
    if (length) {
        randomString = (char*)malloc(sizeof(char) * (length +1));
        if (randomString) {            
            for (int n = 0;n < length;n++) {            
                int key = rand() % (int)(sizeof(charset) -1);
                randomString[n] = charset[key];
            }
            randomString[length] = '\0';
        }
    }
    return randomString;
}
char *cur_id = 0;
void bake(){
    char *id = randstring(16);
    printf("Baked kruassan %s\n",id);fflush(stdout);
    if (cur_id !=0)
        free(cur_id);
    cur_id = id;
}
void Whitelist(char *a){
    for(int i=0; i<strlen(a); i++){
        if ((a[i]>='0' && a[i] <='9') || (a[i]>='A' && a[i]<='Z') || (a[i] >='a' && a[i]<='z'))
            continue;
        a[i]='_';
    }
}
void fillup(char * creme){
    char buf[512];
    if (cur_id == 0){
        printf("No kruassan baked");fflush(stdout);
        return;
    }
    sprintf(buf,"Filling up by %s creme\n",creme);
    printf(buf);fflush(stdout);
    sprintf(buf,"oven/%s",cur_id);
    FILE * f = fopen(buf,"w+");
    fputs(creme,f);
    fclose(f);
}
void eat(char * id){
    char buf[64];
    Whitelist(id);
    sprintf(buf,"oven/%s",id);
    FILE * f = fopen(buf,"r");
    if (f ==0){
            printf("No such kruassan\n");fflush(stdout);
            return;
    }
    fgets(buf,256,f);
    printf(buf);fflush(stdout);
}
int main(){
    char buf[512];
    srand(time(0));
    while(1){
        fgets(buf,512,stdin);
        char * cmd = strtok(buf," \n");
        if (!strcmp(cmd,"bake")){
            bake();
        }
        else if (!strcmp(cmd,"fillup")){
            char * creme = strtok(NULL," \n");
            if (creme!=0)
                fillup(creme);
            else
                printf("No creme provided\n");fflush(stdout);
        }
        else if (!strcmp(cmd,"eat")){
            char * id = strtok(NULL," \n");
            eat(id);
        }
        else if (!strcmp(cmd,"exit")){
            break;
        }
        else{
            printf("Commands:\nbake\nfillup <creme>\neat <id>\n");fflush(stdout);
        }
    }
    return 0;
}
