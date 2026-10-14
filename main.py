from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# CORS 설정: 모든 도메인에서의 요청 허용 (실제 운영 환경에서는 특정 도메인 제한 권장)
CORS(app)

class Node:
    """이진 검색 트리(BST)의 개별 노드를 정의하는 클래스"""
    def __init__(self, key, value=None):
        self.key = key          # 노드의 키값 (정렬 기준)
        self.value = value      # 노드에 저장될 부가 데이터
        self.left = None        # 왼쪽 자식 노드 참조
        self.right = None       # 오른쪽 자식 노드 참조

class BinarySearchTree:
    """이진 검색 트리 구조와 핵심 연산을 관리하는 클래스"""
    def __init__(self):
        self.root = None

    def add(self, key, value=None):
        """트리에 새로운 키를 삽입하고 단계별 기록(steps)을 반환"""
        steps = []
        new_node = Node(key, value)
        
        if not self.root:
            self.root = new_node
            steps.append(f"루트 노드({key})로 설정되었습니다.")
            return True, steps
        
        curr = self.root
        while True:
            if key < curr.key:
                steps.append(f"현재 노드({curr.key})보다 작으므로 왼쪽으로 이동합니다.")
                if not curr.left:
                    curr.left = new_node
                    steps.append(f"왼쪽 자식으로 노드({key})를 삽입했습니다.")
                    break
                curr = curr.left
            elif key > curr.key:
                steps.append(f"현재 노드({curr.key})보다 크므로 오른쪽으로 이동합니다.")
                if not curr.right:
                    curr.right = new_node
                    steps.append(f"오른쪽 자식으로 노드({key})를 삽입했습니다.")
                    break
                curr = curr.right
            else:
                steps.append(f"이미 존재하는 키({key})입니다. 값을 업데이트합니다.")
                curr.value = value
                break
        return True, steps

    def search(self, key):
        """특정 키를 검색하고 탐색 경로를 반환"""
        steps = []
        curr = self.root
        while curr:
            steps.append(f"현재 노드({curr.key}) 확인 중...")
            if key == curr.key:
                steps.append(f"키({key})를 성공적으로 찾았습니다!")
                return curr.value, steps
            elif key < curr.key:
                steps.append(f"찾는 키({key})가 더 작으므로 왼쪽으로 이동합니다.")
                curr = curr.left
            else:
                steps.append(f"찾는 키({key})가 더 크므로 오른쪽으로 이동합니다.")
                curr = curr.right
        steps.append(f"키({key})가 트리에 존재하지 않습니다.")
        return None, steps

    def remove(self, key):
        """특정 키를 가진 노드를 삭제"""
        steps = []
        self.root, deleted = self._remove_recursive(self.root, key, steps)
        return deleted, steps

    def _remove_recursive(self, node, key, steps):
        if not node:
            steps.append(f"키({key})를 찾지 못했습니다.")
            return None, False
        
        if key < node.key:
            steps.append(f"왼쪽 서브트리에서 키({key}) 탐색 중...")
            node.left, deleted = self._remove_recursive(node.left, key, steps)
        elif key > node.key:
            steps.append(f"오른쪽 서브트리에서 키({key}) 탐색 중...")
            node.right, deleted = self._remove_recursive(node.right, key, steps)
        else:
            steps.append(f"삭제할 노드({key})를 발견했습니다.")
            # 자식이 없거나 하나인 경우
            if not node.left:
                steps.append("오른쪽 자식 노드로 교체합니다.")
                return node.right, True
            elif not node.right:
                steps.append("왼쪽 자식 노드로 교체합니다.")
                return node.left, True
            
            # 자식이 둘 다 있는 경우: 오른쪽 서브트리의 최솟값(후속자)으로 대체
            steps.append("자식이 둘이므로 오른쪽 서브트리의 최솟값을 찾아 대체합니다.")
            successor = self._min_node(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right, _ = self._remove_recursive(node.right, successor.key, steps)
            deleted = True
        return node, deleted

    def _min_node(self, node):
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def min_key(self):
        """트리 전체의 최솟값 탐색"""
        if not self.root:
            return None, ["트리가 비어 있습니다."]
        curr = self.root
        steps = [f"루트({curr.key})에서 시작하여 가장 왼쪽 노드로 이동합니다."]
        while curr.left:
            curr = curr.left
            steps.append(f"현재 노드: {curr.key}")
        return curr.key, steps

    def max_key(self):
        """트리 전체의 최댓값 탐색"""
        if not self.root:
            return None, ["트리가 비어 있습니다."]
        curr = self.root
        steps = [f"루트({curr.key})에서 시작하여 가장 오른쪽 노드로 이동합니다."]
        while curr.right:
            curr = curr.right
            steps.append(f"현재 노드: {curr.key}")
        return curr.key, steps

    def dump(self):
        """트리 구조를 계층형 데이터(전위 순회)로 반환하여 시각화 지원"""
        result = []
        def _preorder(node):
            if node:
                result.append({
                    "key": node.key,
                    "left": node.left.key if node.left else None,
                    "right": node.right.key if node.right else None
                })
                _preorder(node.left)
                _preorder(node.right)
        _preorder(self.root)
        return result, ["트리 구조를 덤프(전위 순회)했습니다."]

# 전역 BST 인스턴스 생성
bst = BinarySearchTree()

@app.route('/api/bst', methods=['POST'])
def handle_bst():
    """클라이언트 요청을 받아 BST 연산을 수행하고 결과를 JSON으로 응답"""
    data = request.get_json() or {}
    action = data.get('action')
    key = data.get('key')
    
    if key is not None:
        try:
            key = int(key)
        except ValueError:
            return jsonify({"error": "키 값은 정수여야 합니다."}), 400

    steps = []
    result = None
    
    if action == 'add':
        _, steps = bst.add(key)
    elif action == 'search':
        _, steps = bst.search(key)
    elif action == 'remove':
        _, steps = bst.remove(key)
    elif action == 'min':
        res, steps = bst.min_key()
        result = {"min": res}
    elif action == 'max':
        res, steps = bst.max_key()
        result = {"max": res}
    elif action == 'dump':
        _, steps = bst.dump()
    else:
        return jsonify({"error": "지원하지 않는 작업입니다."}), 400

    tree_structure, _ = bst.dump()
    return jsonify({
        "status": "success",
        "action": action,
        "steps": steps,
        "result": result,
        "tree": tree_structure
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
