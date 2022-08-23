def cell_str(sheet, cell_row, cell_col):
    cell = sheet.cell(cell_row, cell_col)
    v = cell.value
    # XL_CELL_NUMBER == 2, XL_CELL_DATE == 3
    if cell.ctype == 2 or cell.ctype == 3:
        v = int(v)

    return str(v)


def cell_xls_coord_str(row, col):
    """
    return cell coordinate str by zero based row and col
    :param row: zero based row number
    :param col: zero based col number
    :return: cell coordinate str
    """
    return f'({row + 1},{col + 1})'
