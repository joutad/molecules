#include "mol.h"

void atomset( atom *atom, char element[3], double *x, double *y, double *z ) {
    // if (!x || !y || !z || strlen(element) == 0) {
    //     fprintf(stderr, "ATOMSET: PARAMS ARE EMPTY!\n");
    //     exit(1);
    // } 
    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    // if (!x || !y || !z || strlen(element) == 0) {
    //     fprintf(stderr, "ATOMGET: VARIABLES ARE EMPTY!\n");
    //     exit(1);
    // }
}

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    // if (!a1 || !a2 || *epairs <= 0) {
    //     fprintf(stderr, "BONDSET: PARAMS ARE INVALID!\n");
    //     exit(1);
    // } 
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;
    printf("epairs = %d, bond->epairs = %d\n", *epairs, bond->epairs);
    compute_coords(bond);
}

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
    // if (!a1 || !a2 || !epairs) {
        // fprintf(stderr, "BONDGET: VARIABLES ARE EMPTY!\n");
        // exit(1);
    // }
}

void compute_coords( bond *bond ) {
    bond->x1 = bond->atoms[bond->a1].x;
    bond->x2 = bond->atoms[bond->a2].x;

    bond->y1 = bond->atoms[bond->a1].y;
    bond->y2 = bond->atoms[bond->a2].y;
    
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z)/2;

    bond->len = sqrt(pow((bond->x2 - bond->x1), 2) + pow((bond->y2 - bond->y1), 2));

    bond->dx = (bond->x2-bond->x1)/bond->len;
    bond->dy = (bond->y2-bond->y1)/bond->len;
}

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    molecule* newMolecule = malloc(sizeof(molecule));
    if (!newMolecule) {
        fprintf(stderr, "MOLMALLOC: newMolecule IS NULL!\n");
        exit(1);
    }
    
    newMolecule->atom_max = atom_max;
    newMolecule->atom_no = 0;
    newMolecule->atom_ptrs = malloc(sizeof(atom*) * atom_max);
    if (!newMolecule->atom_ptrs) {
        fprintf(stderr, "MOLMALLOC: atom_ptrs IS NULL!\n");
        free(newMolecule);
        exit(1);
    }
    newMolecule->atoms = malloc(sizeof(atom) * atom_max);
    if (!newMolecule->atoms) {
        fprintf(stderr, "MOLMALLOC: atoms IS NULL!\n");
        free(newMolecule->atom_ptrs);
        free(newMolecule);
        exit(1);
    }
    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;
    newMolecule->bond_ptrs = malloc(sizeof(bond*) * bond_max);
    if (!newMolecule->bond_ptrs) {
        fprintf(stderr, "MOLMALLOC: bond_ptrs IS NULL!\n");
        free(newMolecule->atoms);
        free(newMolecule->atom_ptrs);
        free(newMolecule);
        exit(1);
    }
    newMolecule->bonds = malloc(sizeof(bond) * bond_max);
    if (!newMolecule->bonds) {
        fprintf(stderr, "MOLMALLOC: bonds IS NULL!\n");
        free(newMolecule->bond_ptrs);
        free(newMolecule->atoms);
        free(newMolecule->atom_ptrs);
        free(newMolecule);
        exit(1);
    }

    return newMolecule;
}

molecule *molcopy(molecule *src) {
    molecule* copyMolecule = molmalloc(src->atom_max, src->bond_max);
    if (!copyMolecule) {
        fprintf(stderr, "MOLCOPY: copyMolecule IS NULL!\n");
        exit(1);
    }
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(copyMolecule, &src->atoms[i]);
    }
    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond(copyMolecule, &src->bonds[i]);
    }
    copyMolecule->atom_no = src->atom_no;
    copyMolecule->bond_no = src->bond_no;

    return copyMolecule;
}

void molfree( molecule *ptr ) {
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}

void molappend_atom( molecule *molecule, atom *atom ) {
    if (!molecule || !atom) {
        fprintf(stderr, "MOLAPPEND_ATOM: molecule OR atom ARE NULL!\n");
        exit(1);
    }
    if (molecule->atom_max == 0) {
        molecule->atom_max++;
        
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom)*(molecule->atom_max));
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*)*(molecule->atom_max));
        if (!molecule->atoms || !molecule->atom_ptrs) {
            fprintf(stderr, "MOLAPPEND_ATOM: atoms OR atom_ptrs ARE NULL!\n");
            exit(1);
        }
    }
    else if (molecule->atom_max > 0 && molecule->atom_no == molecule->atom_max) {
        molecule->atom_max *= 2;
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom)*(molecule->atom_max));
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*)*(molecule->atom_max));
        if (!molecule->atoms || !molecule->atom_ptrs) {
            fprintf(stderr, "MOLAPPEND_ATOM: atoms OR atom_ptrs ARE NULL!\n");
            exit(1);
        }
    }
    molecule->atoms[molecule->atom_no] = *atom;
    for (int i = 0; i <= molecule->atom_no; i++) {
        molecule->atom_ptrs[i] = &molecule->atoms[i];
    }
    molecule->atom_no++;
}

void molappend_bond( molecule *molecule, bond *bond ) {
    if (!bond || !molecule) {
        fprintf(stderr, "MOLAPPEND_BOND: molecule OR bond ARE NULL\n");
        exit(1);
    }
    if (molecule->bond_max == 0) {
        molecule->bond_max++;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond)*(molecule->bond_max));
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)*(molecule->bond_max));
        if (!molecule->bonds || !molecule->bond_ptrs) {
            fprintf(stderr, "MOLAPPEND_BOND: bonds OR bond_ptrs NULL\n");
            exit(1);
        }
    }
    else if (molecule->bond_max > 0 && molecule->bond_no == molecule->bond_max) {
        molecule->bond_max *= 2;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond)*(molecule->bond_max));
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*)*(molecule->bond_max));
        if (!molecule->bonds || !molecule->bond_ptrs) {
            fprintf(stderr, "MOLAPPEND_BOND: bonds OR bond_ptrs NULL\n");
            exit(1);
        }
    }
    molecule->bonds[molecule->bond_no] = *bond;
    for (int i = 0; i <= molecule->bond_no; i++) {
        molecule->bond_ptrs[i] = &molecule->bonds[i];
    }
    molecule->bond_no++;
}

int compareAtoms(const void *p, const void *q) 
{
    atom* a = (*(atom**)p);
    atom* b = (*(atom**)q);
    if (!a || !b) {
        fprintf(stderr, "ERROR! EITHER a OR b is NULL!\n");
        exit(1);
    }
    double l = a->z;
    double r = b->z;
    if (l < r) {
        return -1;
    }
    else if (l > r) {
        return 1;
    }
    else if (l == r) {
        return 0;
    }
    return 0;
}

int bond_comp( const void *a, const void *b ) {
    bond* i = *(bond**)a;
    bond* j = *(bond**)b;
    if (!a || !b) {
        fprintf(stderr, "ERROR! EITHER a OR b is NULL!\n");
        exit(1);
    }
    double l = (*i).z;
    double r = (*j).z;
    if (l < r) {
        return -1;
    }
    else if (l > r) {
        return 1;
    }
    else if (l == r) {
        return 0;
    }
    return 0;
}

// int compareBonds(const void *p, const void *q) //new name is bond_comp()
// {
//     bond* a = *(bond**)p;
//     bond* b = *(bond**)q;
//     if (!a || !b) {
//         fprintf(stderr, "ERROR! EITHER a OR b is NULL!\n");
//         exit(1);
//     }
//     double l = ((*a).a1->z + (*a).a2->z)/2;
//     double r = ((*b).a1->z + (*b).a2->z)/2;
//     if (l < r) {
//         return -1;
//     }
//     else if (l > r) {
//         return 1;
//     }
//     else if (l == r) {
//         return 0;
//     }
//     return 0;
// }

void molsort( molecule *molecule ) { //MOLSORT NEEDS TO SORT ATOM_PTRS AND BOND_PTRS
    if (!molecule) {
        fprintf(stderr, "MOLSORT: molecule IS NULL!\n");
        exit(1);
    }
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom*), compareAtoms);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond*), bond_comp);
}

//MATRICES
void xrotation( xform_matrix xform_matrix, unsigned short deg ) { //Rx
    double rad = (deg * PI)/180; //radians

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ) { //Ry
    double rad = (deg * PI)/180; //radians

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);
    
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ) { //Rz
    double rad = (deg * PI)/180; //radians

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;
    
    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform( molecule *molecule, xform_matrix matrix ) {
    //3x3 dot 3x1
    for (int i = 0; i < molecule->atom_no; i++) {
        double results[3] = {0, 0, 0};
        for (int j = 0; j < 3; j++) {
            results[j] = (matrix[j][0] * molecule->atoms[i].x) + (matrix[j][1] * molecule->atoms[i].y) + (matrix[j][2] * molecule->atoms[i].z);
        }
        molecule->atoms[i].x = results[0];
        molecule->atoms[i].y = results[1];
        molecule->atoms[i].z = results[2];
    }    

    // for (int i = 0; i < molecule->bond_no; i++) {
    //     compute_coords(molecule->bond_ptrs[i]);
    // }
}
