from PIL import Image
import numpy as np
import scipy.sparse.linalg as splg
import os
import time
from concurrent.futures import ThreadPoolExecutor


class ImagePCA:
    """
    Langkah Pengerjaan:
    1. Konstruksi class ImagePCA
    2. Load data gambar dari path
    3. Preprocess gambar
    4. Fit model PCA
    5. Load query image
    6. Preprocess query image
    7. Find similar images
    
    Contoh:
    ```python
    from ImagePCA import ImagePCA
    
    path = "data/Cover_Art"
    query_path = "query/hind.jpg"

    width = 100
    height = 100
    prep_images, mean_array, filenames = ImagePCA.loadAndPreprocessData(path, width, height)

    pca = ImagePCA()
    pca.fit(prep_images, mean_array)

    with Image.open(query_path) as img:
        query_img = pca.preprocessQueryImage(img, width, height)
        
    similar_images = pca.findSimilarImages(query_img, prep_images, 5)
    print(similar_images) # Output: List[(index, euclidean_distance, similarity)] of 5 most similar images to the query image
    print([filenames[x[0]] for x in similar_images]) # Output: List of image filenames of the 5 most similar images
    
    # Similarity range: 0 to 1
    ```

    Catatan:
    - Pastikan library sudah terinstall
    - X_mean_array adalah mean dari setiap pixel yang di-precompute pada tahap preprocessing
    - U adalah matrix dari k principal components yang dihitung dari SVD
    """
    
    def __init__(self):
        self.U = None
        self.S = None
        self.X_mean_array = None
        self.fit_done = False
        
    @staticmethod
    def loadData(path):
        """
        Returns:
        A list of images as ImageFile from the given path
        """
        images = []
        for filename in os.listdir(path):
            if filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.png'):
                img = Image.open(os.path.join(path, filename))
                images.append(img)
        return images
    
    @staticmethod
    def loadAndPreprocessData(path, width=100, height=100, batch_size=os.cpu_count()//2):
        """
        Returns:
        A tuple containing:
        - A list of standardized images as numpy arrays
        - The mean array
        - A list of image filenames
        """
        start = time.time()
        images = []
        image_paths = []
        filenames = []

        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.png'):
                    image_paths.append(os.path.join(root, filename))
                    filenames.append(filename)

        with ThreadPoolExecutor() as executor:
            for i in range(0, len(image_paths), batch_size):
                batch_paths = image_paths[i:i + batch_size]
                batch_images = list(executor.map(ImagePCA.processImagePath, batch_paths, [width]*len(batch_paths), [height]*len(batch_paths)))
                images.extend(batch_images)

        std_images, mean_array = ImagePCA.stadardizeGrayImages(images)
        end = time.time()
        print("Time to load and preprocess images: ", end - start)
        return (std_images, mean_array, filenames)
    
    @staticmethod
    def processImagePath(image_path, width, height):
        """
        Process a single image path by loading and preprocessing the image.
        """
        with Image.open(image_path) as img:
            img_prep = ImagePCA.preprocessImage(img, width, height)
        return img_prep
    
    @staticmethod
    def saveData(images, path):
        """
        Saves the images to the given path
        """
        for i, img in enumerate(images):
            img.save(os.path.join(path, f'{i}.jpg'))
            
    @staticmethod
    def standardizePixel(pixel, mean):
        return (pixel - mean)

    @staticmethod
    def stadardizeGrayImages(images_array_1d):
        """
        images1D: A non-empty list of 1D images as numpy array of same length
        
        Returns:
        (std_images, mean_array)
        """
        start = time.time()
        N = len(images_array_1d)
        std_images = []

        images_array_1d_np = np.array([img.astype(np.float32) for img in images_array_1d])
        
        mean_array = np.mean(images_array_1d_np, axis=0)
        
        for i in range(N):
            std_images.append(images_array_1d_np[i] - mean_array)
        end = time.time()
        print("Time to standardize images: ", end - start)
        
        return (std_images, mean_array)
            
    @staticmethod
    def preprocessImage(image, width, height):
        """
        Preprocesses the image by converting it to numpy array
        """
        image_resized = image.resize((width, height), Image.NEAREST)
        image_gray = image_resized.convert('L')
        image_1d = np.array(image_gray).flatten()
        return image_1d
    
    def preprocessQueryImage(self, image, width=100, height=100):
        """
        Preprocesses the image by converting it to numpy array and standardizing it
        """
        if not self.fit_done:
            raise ValueError('Fit the model first')
        image_1d = ImagePCA.preprocessImage(image, width, height)
        # std_image = np.zeros(len(image_1d))
        # for i in range(len(image_1d)):
        #     std_image[i] = ImagePCA.standardizePixel(image_1d[i], self.X_mean_array[i])
        std_image = image_1d - self.X_mean_array
        return std_image

    @staticmethod
    def preprocessImages(images, width=100, height=100):
        """
        Preprocesses the images by converting them to numpy arrays
        """
        start_time = time.time()
        images_preprocessed = []
        for img in images:
            img_prep = ImagePCA.preprocessImage(img, width, height)
            images_preprocessed.append(img_prep)
        std_images, mean_array = ImagePCA.stadardizeGrayImages(images_preprocessed)

        end_time = time.time()
        print("Preprocessing time: ", end_time - start_time)
        return (std_images, mean_array)
    
    @staticmethod
    def imagesListToArray(images_array_1d):
        return np.array(images_array_1d)

    @staticmethod
    def covariance(X):
        """
        Returns:
        The covariance matrix of the given matrix X
        """
        N = X.shape[0]
        X_transposed = np.transpose(X)
        cov = np.matmul(X_transposed, X) / N
        return cov
    
    @staticmethod
    def svdKPrincipleComponents(X, k_components=6):
        """
        Returns:
        U_k, S_k, Vt_k
        """
        U_k, S_k, Vt_k = splg.svds(X, k_components, which='LM', return_singular_vectors="u")
        return U_k, S_k, Vt_k
    
    def fit(self, images, mean_array, k_components=10):
        """
        Fits the PCA model to the images
        Args:
        images: List of images as numpy arrays
        n_components: Number of components to keep
        """
        start_time = time.time()
        X = ImagePCA.imagesListToArray(images)
        N = X.shape[0]
        X = np.transpose(X) / np.sqrt(N)
        # cov = ImagePCA.covariance(X)
        
        U, S, Vt = ImagePCA.svdKPrincipleComponents(X, k_components)
        idx = np.argsort(S)[::-1]   # Indices to sort singular values in descending order
        S = S[idx]                  # Sorted singular values
        U = U[:, idx]               # Reorder left singular vectors
        self.U = U
        self.S = S
        self.X_mean_array = mean_array
        self.fit_done = True
        end_time = time.time()
        print("Fitting time: ", end_time - start_time)

    @staticmethod
    def projectToPrincipalComponents(X, U_k):
        """
        Returns:
        The reduced dimensionality representation of X
        """
        Z = np.matmul(X, U_k)
        return Z

    @staticmethod
    def euclideanDistance(q, zi):
        """
        Returns:
        The euclidean distance between the query vector q and the image vector zi
        """
        return np.linalg.norm(q - zi)

    def findSimilarImages(self, prepocessed_query, preprocessed_images, k):
        """    
        Parameters:
        prepocessed_query: The standardized query image as 1D numpy array
        preprocessed_images: A list of standardized images as 1D numpy array
        U_k: The matrix of k principal components
        k: The number of most similar images to return
        
        Returns:
        A list of (indices, euclideanDistance) of the k most similar images to the query image
        """
        start = time.time()
        if not self.fit_done:
            raise ValueError('Fit the model first')
        
        query_Z = ImagePCA.projectToPrincipalComponents(prepocessed_query, self.U)

        distances = []
        for i, img in enumerate(preprocessed_images):
            img_Z = ImagePCA.projectToPrincipalComponents(img, self.U)
            distance = ImagePCA.euclideanDistance(query_Z, img_Z)
            distances.append((i, distance))
        
        distances.sort(key=lambda x: x[1], reverse=False)

        dmean = np.mean([d for i, d in distances])
        distances = [(i, d, 1 / (1 + d/dmean)) for i, d in distances]
        end = time.time()
        print("Time to find similar images: ", end - start)
        return distances[:k]