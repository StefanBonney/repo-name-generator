# src/trie/trie_eos.py
# k-gram Markov eos (end-of-sentence) trie: # k-gram Markov trie: nodes keep children[char] and next_char_counts[next|<EOS>]; add_word() records k-gram→next and final k-gram→<EOS>

#===============================================================
# TrieNode class: holds children and next_char_counts
#===============================================================
class TrieNode:
    def __init__(self):
        # stores only children and next char counts
        # e.g., adding "web": root.children = {'w': node_w}, node_w.children = {'e': node_e}, etc.
        self.children = {}          # char → TrieNode (k-gram path navigation)
        self.next_char_counts = {}  # char → int (next character frequencies for Markov generation)

    #----------------------------------------<getters>
    def get_children(self):     return self.children
    def get_next_counts(self):  return self.next_char_counts

    #----------------------------------------<to_string>
    def __repr__(self):
        return f"Node(children={list(self.get_children().keys())}, next={self.get_next_counts()})"

#===============================================================
# Trie class: holds root node, k value; add_word() to build trie from words
#===============================================================
class Trie:
    def __init__(self, k=2):
        self.root = TrieNode()  # Initial: root.children = {}
        self.k = k              # Markov chain degree = e.g. 2
        # No EOS token in base version - just pure k-gram transitions

    #----------------------------------------<getters>    
    # Get Markov degree
    def get_k(self):    return self.k
    # Get root node
    def get_root(self): return self.root

    #----------------------------------------<add_word>
    def add_word(self, word):
        """
        Add a single word to the trie as k-grams, with next-char transitions
        """
        # --- example run in comments ---
        
        # word = "hello", len(word) = 5, self.k = 2
        # range(len(word) - self.k + 1) = range(5 - 2 + 1) = range(4) = [0, 1, 2, 3]

        word = word.strip()
        if len(word) < self.k:
            return
        n = len(word)

        # Below loop records next_char_counts: "he"→'l', "el"→'l', "ll"→'o'
        # Inside the loop, final k-gram "lo" path created but with empty next_counts as guard prevents recording (terminal k-grams are included but have empty next_counts)

        # CREATE K-GRAM
        for i in range(n - self.k + 1):
            # e.g., k-gram "he": root → children['h'] → children['e'] (creates if missing)
            current_node = self.root    # Reset to root each iteration
            k_gram = word[i:i+self.k]   # i=0: "he", i=1: "el", i=2: "ll", i=3: "lo"
            
            # STORE CHAR PATH WITHIN K-GRAM
            # i=0: chars=['h','e'], i=1: chars=['e','l'], i=2: chars=['l','l'], i=3: chars=['l','o']
            for char in k_gram:
                # if we have already added the char node, fetch it; else create new, then fetch
                if char not in current_node.children:
                    current_node.children[char] = TrieNode()  # iteration 1: root.children = {'h': <TrieNode>}, iteration 2: h.children = {'e': <TrieNode>}
                current_node = current_node.children[char]    
            
            # RECORD NEXT_CHAR 
            # Note! Only at final letter of k-gram (last node reached), i.e. in the example above at {'e': <TrieNode>}
            # and only for non-terminal k-grams
            # we create the transition above even if empty at first, they fill up as more words are added, i.e. k-gram chars=['l','o'], would be guarded against and not have any next char now
            if i + self.k < n:  # Guard: only if there's a next character
                next_char = word[i+self.k] # char that follows the k-gram
                current_node.next_char_counts[next_char] = current_node.next_char_counts.get(next_char, 0) + 1

    #-----------------------------------------<to_string>
    def __str__(self):
        return f"TrieEOS(k={self.k})"