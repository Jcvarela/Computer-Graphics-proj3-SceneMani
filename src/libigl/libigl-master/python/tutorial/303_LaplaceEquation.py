# Add the igl library to the modules search path
import sys, os
sys.path.insert(0, os.getcwd() + "/../")

import igl

V = igl.eigen.MatrixXd()
F = igl.eigen.MatrixXi()

igl.readOFF("../../tutorial/shared/camelhead.off",V,F)

# Find boundary edges
E = igl.eigen.MatrixXi()
igl.boundary_facets(F,E);

# Find boundary vertices
b  = igl.eigen.MatrixXi()
IA = igl.eigen.MatrixXi()
IC = igl.eigen.MatrixXi()

igl.unique(E,b,IA,IC);

# List of all vertex indices
vall  = igl.eigen.MatrixXi()
vin   = igl.eigen.MatrixXi()

igl.coloni(0,V.rows()-1,vall)

# List of interior indices
igl.setdiff(vall,b,vin,IA)

# Construct and slice up Laplacian
L = igl.eigen.SparseMatrixd()
L_in_in = igl.eigen.SparseMatrixd()
L_in_b = igl.eigen.SparseMatrixd()

igl.cotmatrix(V,F,L)
igl.slice(L,vin,vin,L_in_in)
igl.slice(L,vin,b,L_in_b)

# Dirichlet boundary conditions from z-coordinate
bc = igl.eigen.MatrixXd()
Z = V.col(2)
igl.slice(Z,b,bc)

# Solve PDE
solver = igl.eigen.SimplicialLLTsparse(-L_in_in)
Z_in = solver.solve(L_in_b*bc)

# slice into solution
igl.slice_into(Z_in,vin,Z)

# Alternative, short hand
mqwf = igl.min_quad_with_fixed_data()

# Linear term is 0
B = igl.eigen.MatrixXd()
B.setZero(V.rows(),1);

# Empty constraints
Beq = igl.eigen.MatrixXd()
Aeq = igl.eigen.SparseMatrixd()

# Our cotmatrix is _negative_ definite, so flip sign
igl.min_quad_with_fixed_precompute(-L,b,Aeq,True,mqwf)
igl.min_quad_with_fixed_solve(mqwf,B,bc,Beq,Z)

# Pseudo-color based on solution
C = igl.eigen.MatrixXd()
igl.jet(Z,True,C)

# Plot the mesh with pseudocolors
viewer = igl.viewer.Viewer()
viewer.data.set_mesh(V, F)
viewer.core.show_lines = False
viewer.data.set_colors(C)
viewer.launch()
