# -*- coding: utf-8 -*-
from math import ceil
from random import randint

import numpy as np
from matplotlib import colors
from pymol import cmd
from pymol.cgo import *
from pymol.vfont import plain


#############################################################################
#                                                                           #
# drawgridbox.py -- Draw a grid box around a selection                      #
#                                                                           #
# AUTHOR: Loïc Dreano                                                       #
# DATE  : 2023-04-21                                                        #
#                                                                           #
# Acknowledgement:                                                          #
# This script was written based on the drawgridbox.py by Cunliang Geng      #
#                                                                           #
#############################################################################


def get_object_corners(obj_name, view=None):
    if view is None:
        # Get the current camera view
        view = cmd.get_view()

    # get the rotation matrix from the view
    rot_matrix = [[view[0], view[1], view[2]],
                  [view[3], view[4], view[5]],
                  [view[6], view[7], view[8]]]
    # rotation matrix to go back to the original view
    rot_matrix_inv = np.linalg.inv(rot_matrix)

    # Get the coordinates of the atoms in the object
    coords = cmd.get_coords(obj_name)
    t_coord = []
    for coord in coords:
        t_coord.append(get_transform_coord(coord, rot_matrix_inv))
    t_coord = np.array(t_coord, dtype=np.float32)

    # Get the transformed min and max coordinates
    t_x_min, t_x_max = np.min(t_coord[:, 0]), np.max(t_coord[:, 0])
    t_y_min, t_y_max = np.min(t_coord[:, 1]), np.max(t_coord[:, 1])
    t_z_min, t_z_max = np.min(t_coord[:, 2]), np.max(t_coord[:, 2])

    return t_x_min, t_y_min, t_z_min, t_x_max, t_y_max, t_z_max


def drawgridbox(*args, num_grids='(1, 1, 1)', padding=0.0, line_width=0.025, edge_width=0.3,
                line_color='white', edge_color=None, spacing=None, drawAxes=False, save_scene=True, group=True,
                _self=cmd):
    """
    DESCRIPTION
        Given selection, draw a grid box around it.

    USAGE:
        drawgridbox[ box_name [, selection [, num_grids [, padding [, line_width [, edge_width [, line_color [,
         edge_color [, spacing [, drawAxes, save_scene]]]]]]]]]]]

    PARAMETERS:
        box_name,     name of the CGO box, defaults to a randomly generated name

        selection,    the selection to enboxen, defaults to (all)

        num_grids,    number of grids on each axis, defaults to (1, 1, 1)

        padding,      padding of the box, defaults to 0

        line_width    line width, defaults to 0.025

        edge_width,   line width for edges, defaults to 0.3

        line_color,   color of the grid lines except edge, defaults to white

        edge_color,   color of the grid contour, defaults to red

        axes,         draw axes X,Y,Z, from the view to help for orientation

        save_scene,   save the scene for each orientation

        group,        group the selection and the grid box

    RETURNS
        string, the name of the CGO box

    NOTES
        * This function creates a randomly named CGO grid box. The user can
        specify the number of grids on X/Y/Z axis, the width of the lines,
        the padding and also the color.
    """
    if len(args) == 1:
        box_name = None
        selection = args[0]
    elif len(args) == 2:
        box_name = args[0]
        selection = args[1]
    else:
        box_name = None
        selection = '(all)'

    # check if selection exists
    try:
        cmd.select('tmp', selection)
    except:
        print("Error: selection does not exist.")
        return 1

    cmd.delete('tmp')
    r, g, b = colors.to_rgb(line_color)  # get the rgb values of the colors
    # if edge_color is not specified, use the color of the selection
    if edge_color == None:
        color_index = cmd.get_object_color_index(selection)
        if color_index == -1:
            cmd.create('tmp', selection)  # create a temporary object
            color_index = cmd.get_object_color_index('tmp')
            cmd.delete('tmp')
        re, ge, be = cmd.get_color_tuple(color_index)
    else:
        re, ge, be = colors.to_rgb(edge_color)  # get the rgb values of the colors
    nx, ny, nz = num_grids[1:-1].split(',')
    # number of grids on each axis
    lw = float(line_width)  # line width
    lwe = float(edge_width)  # line width for edges

    gridbox = []  # initialize the gridbox
    # enable orthoscopic mode
    cmd.set("orthoscopic", "on")
    view = cmd.get_view()  # get the current view
    # Define the rotation matrix
    rot_matrix = [[view[0], view[1], view[2]],
                  [view[3], view[4], view[5]],
                  [view[6], view[7], view[8]]]
    # get the coordinates of the corners of the selection
    minX, minY, minZ, maxX, maxY, maxZ = get_object_corners(selection, view)  # get the corners of the selection
    # adjust the box dimensions to fit the grid padding
    minX = minX - float(padding)  # add padding to the box
    minY = minY - float(padding)
    minZ = minZ - float(padding)
    maxX = maxX + float(padding)
    maxY = maxY + float(padding)
    maxZ = maxZ + float(padding)
    if spacing == None:
        nX = int(nx)  # number of grids on axis X
        nY = int(ny)  # number of grids on axis Y
        nZ = int(nz)  # number of grids on axis Z
        dX = (maxX - minX) / nX  # grid spacing on axis X
        dY = (maxY - minY) / nY  # grid spacing on axis Y
        dZ = (maxZ - minZ) / nZ  # grid spacing on axis Z
    else:
        dX = float(spacing)  # grid spacing on axis X
        dY = float(spacing)  # grid spacing on axis Y
        dZ = float(spacing)  # grid spacing on axis Z
        nX = ceil((maxX - minX) / dX)  # number of grids on axis X
        nY = ceil((maxY - minY) / dY)  # number of grids on axis Y
        nZ = ceil((maxZ - minZ) / dZ)  # number of grids on axis Z
        maxX = minX + nX * dX  # adjust the box dimensions
        maxY = minY + nY * dY  # to fit the grid spacing
        maxZ = minZ + nZ * dZ  # exactly

    # print size of the box

    # print("Grid box size: {} x {} x {}".format(maxX - minX, maxY - minY, maxZ - minZ))
    # print("Grid spacing: {} x {} x {}".format(dX, dY, dZ))

    # Define the edges parallel to the x-axis
    for j in range(nY + 1):  # loop over the number of grids on the y-axis
        for k in range(nZ + 1):  # loop over the number of grids on the z-axis
            x1, y1, z1 = minX, minY + j * dY, minZ + k * dZ  # define the starting point of the edge
            x2, y2, z2 = maxX, y1, z1  # define the end point of the edge
            # transform the coordinates of the edge to the current view
            x1t, y1t, z1t = get_transform_coord([x1, y1, z1], rot_matrix)
            x2t, y2t, z2t = get_transform_coord([x2, y2, z2], rot_matrix)
            # for the edges in the x-axis, we want to draw the edges of the box with different color
            if (j == 0 and k == 0) or (j == 0 and k == nZ) or (j == nY and k == 0) or (j == nY and k == nZ):
                gridbox += [CYLINDER, x1t, y1t, z1t, x2t, y2t, z2t, lwe / 2, re, ge, be, re, ge, be]
            else:
                gridbox += [CYLINDER, x1t, y1t, z1t, x2t, y2t, z2t, lw / 2, r, g, b, r, g, b]

    # Define the edges parallel to the y-axis
    for i in range(nX + 1):  # loop over the number of grids on the x-axis
        for k in range(nZ + 1):  # loop over the number of grids on the z-axis
            x1, y1, z1 = minX + i * dX, minY, minZ + k * dZ  # define the starting point of the edge
            x2, y2, z2 = x1, maxY, z1  # define the end point of the edge
            # transform the coordinates of the edge to the current view
            x1t, y1t, z1t = get_transform_coord([x1, y1, z1], rot_matrix)
            x2t, y2t, z2t = get_transform_coord([x2, y2, z2], rot_matrix)
            # for the edges in the y-axis, we want to draw the edges of the box with different color
            if (i == 0 and k == 0) or (i == 0 and k == nZ) or (i == nX and k == 0) or (i == nX and k == nZ):
                gridbox += [CYLINDER, x1t, y1t, z1t, x2t, y2t, z2t, lwe / 2, re, ge, be, re, ge, be]
            else:
                gridbox += [CYLINDER, x1t, y1t, z1t, x2t, y2t, z2t, lw / 2, r, g, b, r, g, b]

    # Define the edges parallel to the z-axis
    for i in range(nX + 1):  # loop over the number of grids on the x-axis
        for j in range(nY + 1):  # loop over the number of grids on the y-axis
            x1, y1, z1 = minX + i * dX, minY + j * dY, minZ  # define the starting point of the edge
            x2, y2, z2 = x1, y1, maxZ  # define the end point of the edge
            # transform the coordinates of the edge to the current view
            x1t, y1t, z1t = get_transform_coord([x1, y1, z1], rot_matrix)
            x2t, y2t, z2t = get_transform_coord([x2, y2, z2], rot_matrix)
            # for the edges in the z-axis, we want to draw the edges of the box with different color
            if (i == 0 and j == 0) or (i == 0 and j == nY) or (i == nX and j == 0) or (i == nX and j == nY):
                gridbox += [CYLINDER, x1t, y1t, z1t, x2t, y2t, z2t, lwe / 2, re, ge, be, re, ge, be]
            else:
                gridbox += [CYLINDER, x1t, y1t, z1t, x2t, y2t, z2t, lw / 2, r, g, b, r, g, b]
    if box_name == None:
        box_name = "gridbox_" + str(randint(0, 10000))
        while box_name in cmd.get_names():
            box_name = "gridbox_" + str(randint(0, 10000))
    if drawAxes:
        draw_axes('axes_' + box_name, length=(maxX - minX) / 4, view=True)
    cmd.load_cgo(gridbox, box_name)
    cmd.set_view(view)
    if group is True and selection != '(all)':  # group the selection
        cmd.group('grp_' + selection, '*' + selection + '*' + ' ' + box_name)
        cmd.disable()
        cmd.enable('grp_' + selection + ' ' + '*' + selection + '*' + ' ' + box_name)
    if save_scene:  # create the scene for each orientation
        create_scene(box_name)
        cmd.set_view(view)
    return 0


def draw_axes(name="axes", length=1.0, view=False, axes_coord=False):
    if axes_coord:
        origin = axes_coord[0]
        x_axis = axes_coord[1]
        y_axis = axes_coord[2]
        z_axis = axes_coord[3]
    elif view:
        view = cmd.get_view()
        rot = np.array(view[:9]).reshape(3, 3)
        origin = np.array(view[12:15])
        x_axis = rot[:, 0]
        y_axis = rot[:, 1]
        z_axis = rot[:, 2]
    else:
        rot = np.eye(3)
        origin = np.array([0.0, 0.0, 0.0])
        x_axis = rot[:, 0]
        y_axis = rot[:, 1]
        z_axis = rot[:, 2]
    length = float(length)
    # Calculate the end points of the x, y, and z axes
    x_end = origin + length * x_axis
    y_end = origin + length * y_axis
    z_end = origin + length * z_axis

    # define the parameters of the default axes
    width = length / 20  # cylinder width
    diameter = width * 1.5  # cone base diameter
    height = length / 5  # cone height

    # create the axes object, draw axes with cylinders coloured red, green,
    # blue for X, Y and Z
    axes = [CYLINDER] + list(origin) + list(x_end) + [width] + [1.0, 0.0, 0.0] + [1.0, 0.0, 0.0]
    axes += [CYLINDER] + list(origin) + list(y_end) + [width] + [0.0, 1.0, 0.0] + [0.0, 1.0, 0.0]
    axes += [CYLINDER] + list(origin) + list(z_end) + [width] + [0.0, 0.0, 1.0] + [0.0, 0.0, 1.0]
    # axes += [CONE] + list(x_end) + [x_end[0] + height, x_end[1], x_end[2]] + [diameter] + [0.0] + [1.0, 0.0, 0.0] + [1.0, 0.0, 0.0] + [1.0, 1.0]
    axes += [CONE] + list(x_end) + list(x_end + height * x_axis) + [diameter] + [0.0] + [1.0, 0.0, 0.0] + [1.0, 0.0,
                                                                                                           0.0] + [1.0,
                                                                                                                   1.0]
    axes += [CONE] + list(y_end) + list(y_end + height * y_axis) + [diameter] + [0.0] + [0.0, 1.0, 0.0] + [0.0, 1.0,
                                                                                                           0.0] + [1.0,
                                                                                                                   1.0]
    axes += [CONE] + list(z_end) + list(z_end + height * z_axis) + [diameter] + [0.0] + [0.0, 0.0, 1.0] + [0.0, 0.0,
                                                                                                           1.0] + [1.0,
                                                                                                                   1.0]
    if not axes_coord:
        cyl_text(axes, plain, list(x_end + height * 1.3 * x_axis), 'X', width * 0.6, axes=rot * height)
        cyl_text(axes, plain, list(y_end + height * 1.3 * y_axis), 'Y', width * 0.6, axes=rot * height)
        cyl_text(axes, plain, list(z_end + height * 1.3 * z_axis), 'Z', width * 0.6, axes=rot * height)

    cmd.load_cgo(axes, name)
    if view:
        cmd.set_view(view)
    return axes


def get_transform_coord(coord, rot_matrix=[]):
    # Get the current camera view and orientation matrix
    if len(rot_matrix) == 0:
        view = cmd.get_view()
        # Define the rotation matrix
        rot_matrix = [[view[0], view[1], view[2]],
                      [view[3], view[4], view[5]],
                      [view[6], view[7], view[8]]]
    # Transform the coordinates
    transformed_coord = np.dot(rot_matrix, coord)
    return transformed_coord


def create_scene(box_name):
    # disable the feedback
    cmd.feedback("disable", "scene", "everything")
    # zoom on the box
    cmd.zoom(box_name, buffer=0.5)
    # Create three scene of the grid box for the three axis orientations
    cmd.turn('y', -90)
    cmd.scene(box_name + '_X', 'store')
    cmd.turn('y', 90)
    cmd.turn('x', 90)
    cmd.scene(box_name + '_Y', 'store')
    cmd.turn('x', -90)
    cmd.scene(box_name + '_Z', 'store')

    # Define functions to apply each scene
    def apply_scene_z():
        cmd.scene(box_name + '_Z', 'recall')

    def apply_scene_x():
        cmd.scene(box_name + '_X', 'recall')

    def apply_scene_y():
        cmd.scene(box_name + '_Y', 'recall')

    # bind the scene to the keys F1, F2, F3
    cmd.set_key('F1', apply_scene_x)
    cmd.set_key('F2', apply_scene_y)
    cmd.set_key('F3', apply_scene_z)
    return 0


def apply_scene():
    cmd.scene("my_scene", "recall")  # apply the scene
    return 0


def principal_axes(select='all', show_axes=False, axes_name=None):
    """
    DESCRIPTION :
    Computes principal axes of the selection using pymol
    USAGE :
    principal_axes [select, axes_name]
    PARAMETERS :
    select : selection to compute the principal axes
    axes_name : name of the axes
    RETURNS : information about the principal axes (center, axis1, axis2, axis3)
    """
    # get coordinates of CA atoms
    coords = cmd.get_coords(select)
    # compute center of mass
    center = np.mean(coords, axis=0)
    # center with geometric center
    coord = coords - center
    # compute principal axis matrix
    inertia = np.dot(coord.transpose(), coord)
    e_values, e_vectors = np.linalg.eig(inertia)
    order = np.argsort(e_values)  # sort eigenvalues
    axis3, axis2, axis1 = e_vectors[:, order].transpose()

    axes = [center, axis1, axis2, axis3]  # axes coordinates
    # draw axes
    if show_axes:
        if axes_name == None:
            axes_name = "axes_" + str(randint(0, 10000)) + select
            while axes_name in cmd.get_names():
                axes_name = "axes_" + str(randint(0, 10000)) + select
        # draw axis on pymol
        draw_axes(axes_name, length=10, view=False, axes_coord=axes)
    return axes


def align_principal_axes(select='all', show_axes=False):
    """
    DESCRIPTION :
    Aligns the principal axes of the selection with the origin and normal axes
    USAGE :
    align_principal_axes [select, axes_name
    PARAMETERS :
    select : selection to compute the principal axes
    show_axes : show the axes for debugging
    RETURNS : 0
    """

    center, axis1, axis2, axis3 = principal_axes(select, show_axes, 'Principal_axes' + select + '_before')
    if show_axes:
        draw_axes('axes2', length=10.1, view=False)
    # reset the view so the translation isn't biased by the current view
    cmd.reset()

    # Center the camera at the origin
    cmd.center("origin")

    # translate the selection to the origin
    cmd.translate([-x for x in center], select)

    # create a rotation matrix based on the principal axes
    rotation_matrix = np.array([axis2, axis1, axis3])
    # Check the determinant of the rotation matrix to prevent mirroring
    if np.linalg.det(rotation_matrix) < 0:
        # If the determinant is negative, multiply the first row by -1
        rotation_matrix[0, :] *= -1

    # Create a 4x4 identity matrix
    transformation_matrix = np.identity(4)
    # Replace the upper-left 3x3 part with the rotation matrix
    transformation_matrix[:3, :3] = rotation_matrix
    # Flatten the matrix to a 1D list
    transformation_matrix = list(transformation_matrix.ravel())
    # Apply the rotation to the molecule
    cmd.transform_selection(select, transformation_matrix, homogenous=0)
    if show_axes:
        principal_axes(select, show_axes, 'Principal_axes' + select + '_after')
    cmd.reset()
    return 0


#
# finish_launching()
# cmd.fetch('3shb')
# cmd.fetch('4grv')
# cmd.select('CA', 'chain A and 4grv')
# # align_principal_axes('4grv',show_axes=True)
# drawgridbox('CA',group=False)
# drawgridbox('a', '4grv', line_color = 'white', edge_color = 'pink' )
# drawgridbox('b', 'obj01', line_color = 'white', edge_color = 'cyan' )
# draw_axes('axes', length=10.1, view=False)
# # draw_axes('axes2', length=10.1, view=False)
# drawgridbox ('a', '4grv', inside_color = 'white', outside_color = 'white', drawAxes = True )

cmd.extend("draw_axes", draw_axes)
cmd.extend("drawgridbox", drawgridbox)
cmd.extend("align_principal_axes", align_principal_axes)
