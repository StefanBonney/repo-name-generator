# src/trie/trie_eos.py
# k-gram Markov trie: nodes keep children[char] and next_char_counts[next|<EOS>]; add_word() records k-gram→next and final k-gram→<EOS>

#===============================================================
# TrieNode class: holds children and next_char_counts
#===============================================================
class TrieNode:
    def __init__(self):
        self.children = {}          
        self.next_char_counts = {}  

    #----------------------------------------<getters>
    def get_children(self):     return self.children
    def get_next_counts(self):  return self.next_char_counts

    #----------------------------------------<to_string>
    def __repr__(self):
        return f"Node(children={list(self.get_children().keys())}, next={self.get_next_counts()})"

#===============================================================
# Trie class: holds root node, k value, EOS token; add_word() to build trie from words
#===============================================================
class TrieEOS:
    def __init__(self, k=2):
        self.root = TrieNode()  
        self.k = k              
        self.EOS = "<EOS>"      # End-of-sequence token - models word termination as a learnable transition probability

    #----------------------------------------<getters> 
    # Get Markov degree
    def get_k(self):    return self.k
    # Get root node
    def get_root(self): return self.root

    #----------------------------------------<add_word>
    def add_word(self, word):
        """
        Add a single word to the trie as k-gram -> next-char transitions
        """
        # --- example run in comments ---

        # word = "hello", len(word) = 5, self.k = 2
        # range(len(word) - self.k) = range(5 - 2) = range(3) = [0, 1, 2]
        # Excludes terminal from main loop, therefore no +1 added to range as in trie.py

        word = word.strip()
        if len(word) < self.k:
            return
        n = len(word)

        # Below loop records next_char_counts: "he"→'l', "el"→'l', "ll"→'o'
        # After the loop, add terminal transition: "lo"→"<EOS>"

        # CREATE K-GRAM
        for i in range(n - self.k):
            current_node = self.root    # Reset to root each iteration
            k_gram = word[i:i+self.k]   # i=0: "he", i=1: "el", i=2: "ll"
            next_char = word[i+self.k]  # char that follows the k-gram
            
            # STORE CHAR PATH WITHIN K-GRAM
            # i=0: chars=['h','e'], i=1: chars=['e','l'], i=2: chars=['l','l']
            for char in k_gram:
                if char not in current_node.children:
                    current_node.children[char] = TrieNode()  # Create new node
                current_node = current_node.children[char]    # Move to that node
            
            # RECORD NEXT_CHAR 
            # Record that `next_char` follows this k-gram
            current_node.next_char_counts[next_char] = current_node.next_char_counts.get(next_char, 0) + 1

        # HANDLE TERMINAL K-GRAM TO EOS TRANSITION
        # attach an EOS follower to the FINAL k-gram so we know words can end.
        # for "hello" with k=2, final k-gram is "lo" and we record "lo" -> <EOS>.
        if len(word) >= self.k:
            current_node = self.root
            final_k = word[-self.k:]  # e.g., "lo"
            for char in final_k:
                if char not in current_node.children:
                    current_node.children[char] = TrieNode()
                current_node = current_node.children[char]
            current_node.next_char_counts[self.EOS] = current_node.next_char_counts.get(self.EOS, 0) + 1

    #----------------------------------------<to_string>
    def __str__(self):
        return f"Trie(k={self.k})"

