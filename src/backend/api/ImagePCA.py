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

    width = 200
    height = 200
    prep_images, mean_array = ImagePCA.loadAndPreprocessData(path, width, height)

    pca = ImagePCA()
    pca.fit(prep_images, mean_array)

    with Image.open(query_path) as img:
        query_img = pca.preprocessQueryImage(img, width, height)
        
    similar_images = pca.findSimilarImages(query_img, prep_images, 5)
    print(similar_images)
    
    # Output: List[(index, euclidean_distance, similarity percentage)] of 5 most similar images to the query image
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
    def loadAndPreprocessData(path, width=100, height=100, batch_size=10):
        """
        Returns:
        A list of images as numpy arrays
        """
        start = time.time()
        images = []
        image_paths = []

        # Collect all image paths
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.png'):
                    image_paths.append(os.path.join(root, filename))

        # Batch process images using multithreading
        with ThreadPoolExecutor() as executor:
            for i in range(0, len(image_paths), batch_size):
                batch_paths = image_paths[i:i + batch_size]
                batch_images = list(executor.map(ImagePCA.processImagePath, batch_paths, [width]*len(batch_paths), [height]*len(batch_paths)))
                images.extend(batch_images)

        std_images, mean_array = ImagePCA.stadardizeGrayImages(images)
        end = time.time()
        print("Time to load and preprocess images: ", end - start)
        return (std_images, mean_array)
    
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
        N = len(images_array_1d)
        # len_image = len(images_array_1d[0])
        std_images = []

        images_array_1d_np = np.array([img.astype(np.float32) for img in images_array_1d])
        
        # Pre-calculate mean of each pixel
        mean_array = np.mean(images_array_1d_np, axis=0)
        
        # Standardize each pixel
        for i in range(N):
            # std_image = np.zeros(len_image, dtype=np.float32)
            # for j in range(len_image):
            #     std_image[j] = ImagePCA.standardizePixel(images_array_1d[i][j], mean_array[j])
            # std_images.append(np.array(std_image, dtype=np.float32))
            std_images.append(images_array_1d_np[i] - mean_array)
        
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
    
    def preprocessQueryImage(self, image, width, height):
        """
        Preprocesses the image by converting it to numpy array and standardizing it
        """
        if not self.fit_done:
            raise ValueError('Fit the model first')
        image_1d = ImagePCA.preprocessImage(image, width, height)
        std_image = np.zeros(len(image_1d))
        for i in range(len(image_1d)):
            std_image[i] = ImagePCA.standardizePixel(image_1d[i], self.X_mean_array[i])
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
        # std_images = images_preprocessed
        # mean_array = np.zeros(len(images_preprocessed[0]))
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
        # U_k, S_k, Vt_k = slg.svd(X, full_matrices=False, overwrite_a=True, check_finite=False)
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
        # U = U[:, :k_components]
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
    
    
    def _global_similarity(distance, n_dims, value_range):
        """
        Converts Euclidean distance to a global similarity percentage.

        Parameters:
        - distance (float): Euclidean distance between two points.
        - n_dims (int): Number of dimensions in the embedding space.
        - value_range (tuple): The (min, max) range of each feature.

        Returns:
        - float: Similarity percentage (0 to 100).
        """
        # Calculate the theoretical maximum distance
        a, b = value_range
        d_max = np.sqrt(n_dims * (b - a) ** 2)

        # Normalize the distance
        d_norm = min(max(distance / d_max, 0), 1)

        # Calculate similarity
        similarity = (1 - d_norm) * 100
        return similarity
    
    def _max_theoretical_distance(U, S, k):
        """
        Computes the maximum theoretical Euclidean distance in PCA space.

        Parameters:
        - U: Left singular matrix from SVD.
        - S: Singular values (1D array).
        - k: Number of principal components.

        Returns:
        - float: Maximum theoretical Euclidean distance.
        """
        # Compute eigenvalues (lambda_i) from singular values
        eigenvalues = S[:k] ** 2
        
        # Compute maximum distance
        max_distance = np.sqrt(4 * np.sum(eigenvalues))
        return max_distance

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
        n_dims = self.U.shape[0]
        # max_distance = ImagePCA._max_theoretical_distance(self.U, self.S, n_dims)
        # print(max_distance)
        
        distances = []
        for i, img in enumerate(preprocessed_images):
            img_Z = ImagePCA.projectToPrincipalComponents(img, self.U)
            distance = ImagePCA.euclideanDistance(query_Z, img_Z)
            # distances.append((i, ImagePCA._global_similarity(distance, n_dims, (0, max_distance))))
            distances.append((i, distance))
        
        distances.sort(key=lambda x: x[1], reverse=False)
        # standardized_distances = np.array([d for i, d in distances])
        # standardized_distances = 
        dmax = distances[-1][1]
        # std = np.std([d for i, d in distances])
        distances = [(i, d, 1 / (1 + d/dmax)) for i, d in distances]
        end = time.time()
        print("Time to find similar images: ", end - start)
        return distances[:k]