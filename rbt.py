class Rbtree(object):
    """
    红黑树
    """

    class NodePre(object):
        """
        定义红黑树节点基本属性
        """
        _color = {'red': True, 'black': False}

        def __init__(self, parent=None, color=None, value=None, null=False):
            self.parent = parent
            self.left = None
            self.right = None
            self.color = color
            self.value = value
            self.null = null

        def get_grandparent(self):
            """
            获取节点的祖父节点
            :return:
            """
            p = self.parent
            if p is None:
                return None
            return p.parent

        def get_sibling(self):
            """
            获取节点的兄弟节点
            :return:
            """
            p = self.parent
            if p is None:
                return None
            elif self == p.left:
                return p.right
            else:
                return p.left

        def get_uncle(self):
            """
            获取节点的叔父节点
            :return:
            """
            p = self.parent
            g = self.get_grandparent()

            if g is None:
                return None
            else:
                return p.get_sibling()

        def is_red(self) -> bool:
            """
            判断当前节点颜色是否为红色
            :return:
            """
            return self._color[self.color]

    def __init__(self):
        self.root = self.NodePre(color='black', null=True)

    def _find_minimum_node_(self, sub_lt):
        """
        查找节点子树中的最小节点
        :param sub_lt:
        :return:
        """
        lt = sub_lt
        while not lt.left.null:
            lt = lt.left
        return lt

    def _get_node_parent_(self, value):
        """
        找到新节点插入合适位置的父节点
        :param value:
        :return:
        """
        rt = self.root
        q = None
        while not rt.null:  # 遍历树
            q = rt  # 确保遍历结束前获取到父节点
            if rt.value > value:  # 如果当前节点值大于给定值则往左子树查找
                rt = rt.left
            else:  # 反之则往右子树查找
                rt = rt.right
        return q

    def _get_node_(self, value):
        """
        获取与给定值相等的节点
        :param value:
        :return:
        """
        rt = self.root
        while not rt.null:
            if rt.value > value:
                rt = rt.left
            elif rt.value < value:
                rt = rt.right
            else:  # 如果相等，直接返回该值的节点
                return rt
        return None

    def _left_rotate_(self, node):
        """
        节点左旋转，比如：
          x           y
           \        /
            y  ->  x
          /        \
         z          z
        这里 x 就是 node。
        :param node:
        :return:
        """
        x = node
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x.parent.left == x:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate_(self, node):
        """
        节点右旋转，比如：
           x         y
          /           \
         y     ->     x
          \          /
           z       z
        :param node:
        :return:
        """
        x = node
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x.parent.left == x:
            x.parent.left = y
        else:
            x.parent.right = y
        y.right = x
        x.parent = y

    def _leftright_rotate_(self, node):
        """
        左右双旋转

        :param node:
        :return:
        """
        x = node
        y = x.left
        self._left_rotate_(y)
        self._right_rotate_(x)

    def _rightleft_rotate_(self, node):
        """
        右左双旋转

        :param node:
        :return:
        """
        x = node
        y = x.right
        self._right_rotate_(y)
        self._left_rotate_(x)

    def _transplant_(self, node, f_node):
        if node.parent is None:
            self.root = f_node
        elif node == node.parent.left:
            node.parent.left = f_node
        else:
            node.parent.right = f_node

        if f_node:
            f_node.parent = node.parent

    def _insert_fixup_(self, node):
        """
        每次插入节点后确保红黑树性质不被破坏
        :param node:
        :return:
        """
        while node.parent and node.parent.is_red():
            g = node.get_grandparent()
            if node.parent == g.left:
                u = node.get_uncle()
                if u.is_red():
                    node.parent.color = 'black'
                    u.color = 'black'
                    g.color = 'red'
                    node = g
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate_(node)
                    node.parent.color = 'black'
                    g.color = 'red'
                    self._right_rotate_(g)
            else:
                u = node.get_uncle()
                if u.is_red():
                    node.parent.color = 'black'
                    u.color = 'black'
                    g.color = 'red'
                    node = g
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate_(g)
                    node.parent.color = 'black'
                    g.color = 'red'
                    self._left_rotate_(g)
            if node == self.root:
                break
        self.root.color = 'black'

    def _remove_fixup_(self, node):
        """
        删除一类节点后确保红黑树性质不被破坏
        删除的维护代码很复杂，因为会导致红黑树性质被破坏的情况有 4 种
        1.删除一个黑节点，其有 1 个红色孩子（左或右）
        2.删除一个黑节点，其有 2 个红色孩子
        3.删除一个黑色叶节点，导致破坏性质 5 ：对于每个节点，从该节点到其所有叶节点的简单路径上，均包含相同数目的黑色节点。
        4.删除一个红节点，其替换节点颜色为黑色（因为红节点必定有两个黑色子节点，所以如果替换节点也为黑色，替换会导致性质 5 被破坏）
        :param node:
        :return:
        """
        # 情况 1 时，不进入循环，直接将其节点染为黑色即可
        while node != self.root and not node.is_red():
            if node == node.parent.left:  # 如果维护节点是左孩子
                s = node.get_sibling()
                if s.is_red():
                    s.color = 'black'
                    node.parent.color = 'red'
                    self._left_rotate_(node.parent)
                    s = node.parent.right
                if not s.left.is_red() and not s.right.is_red():
                    s.color = 'red'
                    node = node.parent
                else:
                    if not s.right.is_red():
                        s.left.color = 'black'
                        s.color = 'red'
                        self._right_rotate_(s)
                        s = node.parent.right
                    s.color = node.parent.color
                    node.parent.color = 'black'
                    s.right.color = 'black'
                    self._left_rotate_(node.parent)
                    node = self.root
            else:  # 和上面基本一样只是操作相反
                s = node.parent.left
                if s.is_red():
                    s.color = 'black'
                    node.parent.color = 'red'
                    self._right_rotate_(node.parent)
                    s = node.parent.left
                if not s.left.is_red() and not s.right.is_red():
                    s.color = 'red'
                    node = node.parent
                else:
                    if not s.left.is_red():
                        s.right.color = 'black'
                        s.color = 'red'
                        self._left_rotate_(s)
                        s = node.parent.left
                    s.color = node.parent.color
                    node.parent.color = 'black'
                    s.left.color = 'black'
                    self._right_rotate_(node.parent)
                    node = self.root
        node.color = 'black'

    def insert(self, value):
        """
        插入节点，和二叉树的插入操作几乎差不多
        :param value:
        :return:
        """
        q = self._get_node_parent_(value)
        nn = self.NodePre(q, 'red', value)
        lleaf = self.NodePre(nn, 'black', null=True)
        rleaf = self.NodePre(nn, 'black', null=True)
        if q is None:
            self.root = nn
        elif q.value > value:
            q.left = nn
        else:
            q.right = nn
        nn.left = lleaf
        nn.right = rleaf
        self._insert_fixup_(nn)

    def remove(self, value):
        """
        删除节点
        :param value:
        :return:
        """
        q = self._get_node_(value)
        if q is None:
            raise Exception('不存在具有值 %s 的节点!' % value)
        color = q.color
        if q.left.null:
            fix_node = q.right
            self._transplant_(q, q.right)
        elif q.right.null:
            fix_node = q.left
            self._transplant_(q, q.left)
        else:
            min_slt = self._find_minimum_node_(q.right)
            color = min_slt.color
            fix_node = min_slt.right
            if min_slt.parent == q:
                if fix_node:
                    fix_node.parent = min_slt
            else:
                self._transplant_(min_slt, min_slt.right)
                min_slt.right = q.right
                if min_slt.right:
                    min_slt.right.parent = min_slt
            self._transplant_(q, min_slt)
            min_slt.left = q.left
            if min_slt.left:
                min_slt.left.parent = min_slt
            min_slt.color = q.color
        if color == 'black':
            self._remove_fixup_(fix_node)

    def _print_(self, rt):
        """
        中序遍历
        :param rt:
        :return:
        """
        if not rt.null:
            self._print_(rt.left)
            print(rt.value, '-' * 4, rt.color)
            self._print_(rt.right)

    def output(self):
        """
        输出树中所有节点及颜色
        :return:
        """
        self._print_(self.root)


if __name__ == '__main__':
    rbt = Rbtree()
    rbt.insert(101)
    rbt.insert(96)
    rbt.insert(87)
    rbt.insert(79)
    rbt.insert(82)
    rbt.insert(65)
    rbt.insert(41)
    rbt.insert(38)
    print('-' * 50)
    rbt.output()
    print(rbt.root.value, '-' * 4, 'root')
    rbt.insert(31)
    rbt.insert(12)
    print('-' * 50)
    rbt.output()
    print(rbt.root.value, '-' * 4, 'root')
    rbt.insert(19)
    rbt.insert(8)
    print('-' * 50)
    rbt.output()
    print(rbt.root.value, '-' * 4, 'root')
    print('-'*50)
    rbt.remove(8)
    rbt.output()
    print('-' * 50)
    rbt.remove(12)
    rbt.output()
    print('-' * 50)
    rbt.remove(19)
    rbt.output()
