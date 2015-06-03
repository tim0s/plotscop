int main () {

	const int arraysize = 1000;
	double sum;
	int* A = (int*) malloc(arraysize*sizeof(int));
	int* B = (int*) malloc(arraysize*sizeof(double));

	memset(&A[0], 0, arraysize*sizeof(int));

	for(int i=0; i<arraysize; i++) {
		B[42] += A[i];		
	}
	
	printf("sum=%d\n", B[42]);	

}
