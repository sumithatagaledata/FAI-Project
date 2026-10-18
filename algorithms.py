"""
Data Structures and Algorithms (DSA) Module for AI-Based Resume Screening System.

This module contains explicit implementations of fundamental DSA concepts:
1. Custom Sorting Algorithms: Merge Sort and Quick Sort (for candidate ranking)
2. Custom Heap / Priority Queue: Max-Heap (for Top-K candidate retrieval)
3. Custom Searching Algorithms: Binary Search and Linear Search
4. Custom Indexing Data Structure: Inverted Index (Hash Map based for skill lookups)
5. Set Operations: Set Union, Intersection, and Difference (for skill gap analysis)
"""

from typing import List, Dict, Any, Callable, Optional


# ==========================================
# 1. SORTING ALGORITHMS
# ==========================================

def merge_sort(arr: List[Any], key: Optional[Callable[[Any], Any]] = None, reverse: bool = False) -> List[Any]:
    """
    Merge Sort Algorithm implementation (O(N log N) time complexity, Stable).
    
    Args:
        arr: The list of elements to sort.
        key: A function to extract a comparison key from each element.
        reverse: If True, sort in descending order (highest score first).
        
    Returns:
        A new sorted list.
    """
    if len(arr) <= 1:
        return arr[:]
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key=key, reverse=reverse)
    right = merge_sort(arr[mid:], key=key, reverse=reverse)
    
    return _merge(left, right, key, reverse)


def _merge(left: List[Any], right: List[Any], key: Optional[Callable[[Any], Any]], reverse: bool) -> List[Any]:
    merged = []
    i = j = 0
    
    def get_val(item):
        return key(item) if key else item
    
    while i < len(left) and j < len(right):
        val_l = get_val(left[i])
        val_r = get_val(right[j])
        
        # Compare based on reverse flag
        if (val_l >= val_r if reverse else val_l <= val_r):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(arr: List[Any], key: Optional[Callable[[Any], Any]] = None, reverse: bool = False) -> List[Any]:
    """
    Quick Sort Algorithm implementation (O(N log N) average time complexity).
    
    Args:
        arr: The list of elements to sort.
        key: A function to extract a comparison key from each element.
        reverse: If True, sort in descending order.
        
    Returns:
        A new sorted list.
    """
    items = arr[:]
    _quick_sort_helper(items, 0, len(items) - 1, key, reverse)
    return items


def _quick_sort_helper(arr: List[Any], low: int, high: int, key: Optional[Callable[[Any], Any]], reverse: bool):
    if low < high:
        pi = _partition(arr, low, high, key, reverse)
        _quick_sort_helper(arr, low, pi - 1, key, reverse)
        _quick_sort_helper(arr, pi + 1, high, key, reverse)


def _partition(arr: List[Any], low: int, high: int, key: Optional[Callable[[Any], Any]], reverse: bool) -> int:
    def get_val(item):
        return key(item) if key else item
    
    pivot = get_val(arr[high])
    i = low - 1
    
    for j in range(low, high):
        val = get_val(arr[j])
        condition = (val >= pivot) if reverse else (val <= pivot)
        if condition:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# ==========================================
# 2. PRIORITY QUEUE / MAX-HEAP
# ==========================================

class CandidateMaxHeap:
    """
    Max-Heap data structure for ranking and retrieving Top-K candidates efficiently.
    Heap Property: Parent value is always >= child values.
    Time Complexity: Insertion O(log N), Extraction O(log N).
    """
    
    def __init__(self, key: Optional[Callable[[Any], Any]] = None):
        self.heap: List[Any] = []
        self.key = key or (lambda x: x)
        
    def _val(self, index: int) -> Any:
        return self.key(self.heap[index])
        
    def _parent(self, i: int) -> int:
        return (i - 1) // 2
        
    def _left_child(self, i: int) -> int:
        return 2 * i + 1
        
    def _right_child(self, i: int) -> int:
        return 2 * i + 2
        
    def push(self, item: Any):
        """Insert a candidate into the max heap."""
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)
        
    def pop(self) -> Optional[Any]:
        """Extract and return the candidate with the highest match score."""
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
            
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root
        
    def peek(self) -> Optional[Any]:
        """Return the top candidate without removing."""
        return self.heap[0] if self.heap else None
        
    def _sift_up(self, i: int):
        parent = self._parent(i)
        while i > 0 and self._val(i) > self._val(parent):
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            i = parent
            parent = self._parent(i)
            
    def _sift_down(self, i: int):
        max_idx = i
        left = self._left_child(i)
        right = self._right_child(i)
        
        if left < len(self.heap) and self._val(left) > self._val(max_idx):
            max_idx = left
            
        if right < len(self.heap) and self._val(right) > self._val(max_idx):
            max_idx = right
            
        if max_idx != i:
            self.heap[i], self.heap[max_idx] = self.heap[max_idx], self.heap[i]
            self._sift_down(max_idx)
            
    def get_top_k(self, k: int) -> List[Any]:
        """Extract the top-K highest-ranked candidates."""
        temp_heap = CandidateMaxHeap(self.key)
        temp_heap.heap = self.heap[:]
        top_k = []
        for _ in range(min(k, len(temp_heap.heap))):
            top_k.append(temp_heap.pop())
        return top_k

    def size(self) -> int:
        return len(self.heap)


# ==========================================
# 3. SEARCHING ALGORITHMS
# ==========================================

def binary_search_by_name(sorted_candidates: List[Dict[str, Any]], target_name: str) -> Optional[Dict[str, Any]]:
    """
    Binary Search Algorithm (O(log N)) to find a candidate by name in a sorted list.
    Prerequisite: candidates must be sorted by name in ascending alphabetical order.
    """
    low = 0
    high = len(sorted_candidates) - 1
    target = target_name.strip().lower()
    
    while low <= high:
        mid = (low + high) // 2
        cand_name = sorted_candidates[mid].get("name", "").strip().lower()
        
        if cand_name == target:
            return sorted_candidates[mid]
        elif cand_name < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return None


def linear_search_candidates(candidates: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Linear Search Algorithm (O(N)) across multiple fields (name, email, skills, education).
    """
    if not query:
        return candidates
        
    q = query.strip().lower()
    results = []
    
    for cand in candidates:
        name = cand.get("name", "").lower()
        email = cand.get("email", "").lower()
        education = cand.get("education", "").lower()
        skills = [s.lower() for s in cand.get("skills", [])]
        
        if (q in name or q in email or q in education or any(q in s for s in skills)):
            results.append(cand)
            
    return results


# ==========================================
# 4. INVERTED INDEX (HASH MAP)
# ==========================================

class SkillInvertedIndex:
    """
    Inverted Index data structure mapping skills to candidate IDs for O(1) lookup.
    Example:
      "python" -> {cand_1, cand_2, cand_5}
      "sql"    -> {cand_2, cand_3}
    """
    
    def __init__(self):
        # Hash Map: key = skill_name (lowercase), value = Set of candidate indices/IDs
        self.index: Dict[str, set] = {}
        
    def add_candidate(self, candidate_id: Any, skills: List[str]):
        """Index a candidate by all their detected skills."""
        for skill in skills:
            s_clean = skill.strip().lower()
            if s_clean not in self.index:
                self.index[s_clean] = set()
            self.index[s_clean].add(candidate_id)
            
    def search_by_skill(self, skill: str) -> set:
        """Retrieve all candidate IDs that have a given skill."""
        return self.index.get(skill.strip().lower(), set())
        
    def search_all_skills(self, skills: List[str]) -> set:
        """Find candidate IDs that match ANY of the requested skills (Union)."""
        result = set()
        for s in skills:
            result.update(self.search_by_skill(s))
        return result


# ==========================================
# 5. SET OPERATIONS (SKILL GAP ANALYSIS)
# ==========================================

def analyze_skill_gap(job_skills: List[str], candidate_skills: List[str]) -> Dict[str, List[str]]:
    """
    Performs Mathematical Set Operations:
    - Matched Skills   = Job Skills ∩ Candidate Skills (Intersection)
    - Missing Skills   = Job Skills - Candidate Skills (Difference)
    - Additional Skills= Candidate Skills - Job Skills (Difference)
    """
    job_set = {s.strip().lower(): s.strip() for s in job_skills if s.strip()}
    cand_set = {s.strip().lower(): s.strip() for s in candidate_skills if s.strip()}
    
    matched_keys = set(job_set.keys()).intersection(set(cand_set.keys()))
    missing_keys = set(job_set.keys()).difference(set(cand_set.keys()))
    additional_keys = set(cand_set.keys()).difference(set(job_set.keys()))
    
    # Return formatted casing
    return {
        "matched": [job_set[k] for k in matched_keys],
        "missing": [job_set[k] for k in missing_keys],
        "additional": [cand_set[k] for k in additional_keys]
    }
