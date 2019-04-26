import math
class MinHeap:
    def __init__(self):
        self.size = 0
        self.capacity = 1000
        self.array = [None] * self.capacity

    def insert(self,item):
        
        self.array[self.size] = item
        #print("Inserting {0} at index {1}".format(item[0],self.size))
        self.siftup(self.size)
    
        self.size += 1
        #print("Size increased to {0}".format(self.size))
        if self.size >= self.capacity:
            #print("Resizing heap")
            self.capacity = self.capacity * 2
            #print(self.capacity)
            new_arr = [None] * self.capacity
            #print(new_arr)
            new_arr[:len(self.array)] = self.array
            self.array = new_arr
            #print(self.array)
    def siftup(self,index):
        #print("Moving {0} to correct position".format(self.array[index]))
        parent = max(0,math.floor((index-1)/2))
        #print("{0} has parent {1} at index {2}".format(self.array[index],self.array[parent],parent))
        if self.array[index][1] < self.array[parent][1]:
                #print("Since {0} has lower score than {1}, they should be swapped.".format(self.array[index],self.array[parent]))
                self.swap(index, parent)
                self.siftup(parent)
    def extract(self):
        ret_val = self.array[0]
        self.size -= 1
        self.swap(0,self.size)
        
        self.siftdown(0)
        return ret_val
    
    def siftdown(self,index):
        left = (index * 2) + 1
        right = (index * 2) + 2
        smallest = index
            
        if left <= self.size and self.array[left] != None:
            if self.array[left][1] < self.array[smallest][1]:
                smallest = left

        if right <= self.size:
            if self.array[right][1] < self.array[smallest][1]:
                smallest = right

        if smallest != index:
            self.swap(index,smallest)
            self.siftdown(smallest)
    def swap(self,first, second):
            #print("Swapping {0} and {1}".format(self.array[first],self.array[second]))
            tmp = self.array[first]
            self.array[first] = self.array[second]
            self.array[second] = tmp
