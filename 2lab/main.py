
import math
from itertools import islice, count, chain
from functools import reduce, wraps
 
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
 
def distance(p1, p2):
    return math.dist(p1, p2)
 
def polygon_area(poly):
    n = len(poly)
    s = 0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2
 
def polygon_perimeter(poly):
    return sum(distance(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
 
def min_side(poly):
    return min(distance(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
 
def max_side(poly):
    return max(distance(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
 
def centroid(poly):
    x = sum(p[0] for p in poly) / len(poly)
    y = sum(p[1] for p in poly) / len(poly)
    return x, y
 
def visualize(polygons, title="Polygons"):
    fig, ax = plt.subplots(figsize=(10, 8))
 
    for poly in polygons:
        patch = MplPolygon(poly, closed=True, fill=False, edgecolor="black")
        ax.add_patch(patch)
 
    ax.set_aspect("equal")
    ax.autoscale()
    ax.set_title(title)
    plt.grid(True)
    plt.show()
 
def gen_rectangle(width=2, height=1, step=4):
    for i in count(0):
        x = i * step
        yield (
            (x, 0),
            (x + width, 0),
            (x + width, height),
            (x, height),
        )
 
def gen_triangle(side=2, step=4):
    h = side * math.sqrt(3) / 2
    for i in count(0):
        x = i * step
        yield (
            (x, 0),
            (x + side, 0),
            (x + side / 2, h),
        )
def gen_hexagon(side=1, step=4):
    for i in count(0):
        cx = i * step
        cy = 0
        pts = tuple(
            (
                cx + side * math.cos(math.radians(60 * k)),
                cy + side * math.sin(math.radians(60 * k)),
            )
            for k in range(6)
        )
        yield pts
 
def tr_translate(poly, dx=0, dy=0):
    return tuple((x + dx, y + dy) for x, y in poly)
 
def tr_rotate(poly, angle=0, center=(0, 0)):
    cx, cy = center
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
 
    def rotate_point(p):
        x, y = p
        x -= cx
        y -= cy
        xr = x * cos_a - y * sin_a
        yr = x * sin_a + y * cos_a
        return xr + cx, yr + cy
 
    return tuple(map(rotate_point, poly))
 
def tr_symmetry(poly, axis="x"):
    if axis == "x":
        return tuple((x, -y) for x, y in poly)
    if axis == "y":
        return tuple((-x, y) for x, y in poly)
    if axis == "origin":
        return tuple((-x, -y) for x, y in poly)
    return poly
 
def tr_homothety(poly, k=1.0, center=(0, 0)):
    cx, cy = center
    return tuple((cx + k * (x - cx), cy + k * (y - cy)) for x, y in poly)
 
def flt_convex_polygon(poly):
    n = len(poly)
    if n < 3:
        return False    
def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
 
    signs = []
    for i in range(n):
        c = cross(poly[i], poly[(i + 1) % n], poly[(i + 2) % n])
        if c != 0:
            signs.append(c > 0)
 
    return all(signs) or not any(signs)
 
def flt_square(poly, max_area_value):
    return polygon_area(poly) < max_area_value
 
def flt_short_side(poly, max_len):
    return min_side(poly) < max_len
 
def point_inside_convex(poly, point):
    x, y = point
    n = len(poly)
    prev = None
 
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        sign = cross >= 0
        if prev is None:
            prev = sign
        elif prev != sign:
            return False
    return True
 
def flt_point_inside(poly, point):
    return flt_convex_polygon(poly) and point_inside_convex(poly, point)
 
def decorator_filter(filter_func, *f_args, **f_kwargs):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return filter(lambda p: filter_func(p, *f_args, **f_kwargs), result)
 
        return wrapper
 
    return outer
 
def decorator_transform(transform_func, *t_args, **t_kwargs):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return map(lambda p: transform_func(p, *t_args, **t_kwargs), result)
 
        return wrapper
 
    return outer

flt_square_dec = lambda max_area_value: decorator_filter(flt_square, max_area_value)
flt_short_side_dec = lambda max_len: decorator_filter(flt_short_side, max_len)
tr_translate_dec = lambda dx, dy: decorator_transform(tr_translate, dx, dy)
tr_rotate_dec = lambda angle: decorator_transform(tr_rotate, angle)
 
def agr_origin_nearest(polygons):
    return reduce(
        lambda a, b: a if distance(centroid(a), (0, 0)) < distance(centroid(b), (0, 0)) else b,
        polygons,
    )
 
def agr_max_side(polygons):
    return reduce(lambda acc, p: max(acc, max_side(p)), polygons, 0)
 
def agr_min_area(polygons):
    return reduce(lambda acc, p: min(acc, polygon_area(p)), polygons, float("inf"))
 
def agr_perimeter(polygons):
    return reduce(lambda acc, p: acc + polygon_perimeter(p), polygons, 0)
 
def agr_area(polygons):
    return reduce(lambda acc, p: acc + polygon_area(p), polygons, 0)
 
def zip_polygons(*polygons):
    min_len = min(len(p) for p in polygons)
    result = []
    for i in range(min_len):
        result.extend(p[i] for p in polygons)
    return tuple(result)
 
def count_2D(start=0, step_x=1, step_y=1):
    for i in count(start):
        yield i * step_x, i * step_y
 
def zip_tuple(*iters):
    return zip(*iters)
 
def make_strip(generator_func, n=7, dx=0, dy=0, angle=0):
    base = list(islice(generator_func(), n))
    moved = list(map(lambda p: tr_translate(p, dx, dy), base))
    rotated = list(map(lambda p: tr_rotate(p, angle), moved))
    return rotated
 
if __name__ == "__main__":
    rects = list(islice(gen_rectangle(width=2, height=1, step=3), 7))
    tris = list(islice(gen_triangle(side=2, step=3), 7))    
hexs = list(islice(gen_hexagon(side=1, step=3.2), 7))
 
    visualize(rects, "7 прямоугольников")
    visualize(tris, "7 треугольников")
    visualize(hexs, "7 шестиугольников")
 
    strip1 = make_strip(gen_rectangle, 7, dy=-2, angle=30)
    strip2 = make_strip(gen_rectangle, 7, dy=1, angle=30)
    strip3 = make_strip(gen_rectangle, 7, dy=4, angle=30)
 
    visualize(chain(strip1, strip2, strip3), "Три параллельные ленты")
 
    cross1 = make_strip(gen_rectangle, 6, dx=-4, dy=1, angle=35)
    cross2 = make_strip(gen_rectangle, 6, dx=-4, dy=1, angle=-35)
 
    visualize(chain(cross1, cross2), "Две пересекающиеся ленты")
 
    tri_up = list(islice(gen_triangle(side=2, step=3), 7))
    tri_up = list(map(lambda p: tr_translate(p, 0, 2), tri_up))
 
    tri_down = list(map(lambda p: tr_symmetry(p, "x"), tri_up))
 
    visualize(chain(tri_up, tri_down), "Симметричные ленты треугольников")
 
    base_quad = ((0, 0), (1.2, 0.4), (1.0, 1.0), (0.0, 0.6))
 
    scaled = []
    for k in [1, 1.8, 2.6, 3.4, 4.2]:
        p = tr_homothety(base_quad, k, center=(0, 0))
        p = tr_rotate(p, 35)
        scaled.append(p)
 
    mirror_scaled = list(map(lambda p: tr_symmetry(p, "origin"), scaled))
 
    visualize(chain(scaled, mirror_scaled), "Четырёхугольники разного масштаба")
 
    many = list(islice(gen_rectangle(width=1, height=1), 15))
    filtered = list(filter(lambda p: flt_short_side(p, 1.5), many))
    visualize(filtered[:6], "Фильтр по короткой стороне")
 
    @tr_translate_dec(0, 8)
    @flt_square_dec(3)
    def decorated_polygons():
        return gen_rectangle(width=1, height=2)
 
    result = list(islice(decorated_polygons(), 6))
    visualize(result, "Декораторы")
 
    print("Максимальная сторона:", agr_max_side(rects))
    print("Суммарная площадь:", agr_area(rects))
    print("Суммарный периметр:", agr_perimeter(rects))