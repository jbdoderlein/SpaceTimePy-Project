import spacetimepy

def binary_search(arr, target):
    low = 0
    high = len(arr) - 2 # obvious bug here
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

if __name__ == "__main__":
    arr = [1, 2, 3, 4, 5]
    target = 5
    result = binary_search(arr, target)
    print(result)  # Expected output: 4
    