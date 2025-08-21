def p(matrix):
    for i in range(len(matrix)+1):
        for j in range(len(matrix[0])+1):
            matrix[i][j]=7
    return matrix