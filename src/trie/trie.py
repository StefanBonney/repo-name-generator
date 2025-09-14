# src/trie/trie.py
# k-gram Markov trie: nodes keep children[char] and next_char_counts[next|<EOS>]; add_word() records k-gram→next and final k-gram→<EOS>

class TrieNode:
    def __init__(self):
        self.children = {}          # Maps character -> TrieNode (for walking the k-gram path)
        self.next_char_counts = {}  # Counts of next characters that follow this k-gram (Markov part)
        
    def __repr__(self):
        return f"Node(children={list(self.children.keys())}, next={self.next_char_counts})"


class Trie:
    def __init__(self, k=2):
        self.root = TrieNode()  # Initial: root.children = {}
        self.k = k              # Markov chain degree = 2
        self.EOS = "<EOS>"      # End-of-sequence token - models word termination as a learnable transition probability
        
    def add_word(self, word):
        """Add a single word to the trie as k-gram -> next-char transitions"""
        word = word.strip()
        if len(word) < self.k:
            return
        n = len(word)

        # --- example run in comments ---
        # word = "hello", len(word) = 5, self.k = 2
        # range(len(word) - self.k) = range(5 - 2) = range(3) = [0, 1, 2]
        # This loop records transitions "he"->'l', "el"->'l', "ll"->'o'
        # After the loop, add terminal transition: "lo"→"<EOS>"

        for i in range(n - self.k):
            current_node = self.root    # Reset to root each iteration
            k_gram = word[i:i+self.k]   # i=0: "he", i=1: "el", i=2: "ll"
            next_char = word[i+self.k]  # char that follows the k-gram
            
            # Navigate/create path for the k-gram
            # i=0: chars=['h','e'], i=1: chars=['e','l'], i=2: chars=['l','l']
            for char in k_gram:
                if char not in current_node.children:
                    current_node.children[char] = TrieNode()  # Create new node
                current_node = current_node.children[char]    # Move to that node
            
            # Record that `next_char` follows this k-gram
            current_node.next_char_counts[next_char] = current_node.next_char_counts.get(next_char, 0) + 1

        # Also attach an EOS follower to the FINAL k-gram so we know words can end.
        # For "hello" with k=2, final k-gram is "lo" and we record "lo" -> <EOS>.
        if len(word) >= self.k:
            current_node = self.root
            final_k = word[-self.k:]  # e.g., "lo"
            for char in final_k:
                if char not in current_node.children:
                    current_node.children[char] = TrieNode()
                current_node = current_node.children[char]
            current_node.next_char_counts[self.EOS] = current_node.next_char_counts.get(self.EOS, 0) + 1


# --- minimal test ---
#trie = Trie(k=2)
#test_words = ["hello", "help"]

#for w in test_words:
#    trie.add_word(w)