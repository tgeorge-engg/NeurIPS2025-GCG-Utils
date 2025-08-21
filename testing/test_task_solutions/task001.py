def p(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            matrix[i][j]+=1
    return matrix