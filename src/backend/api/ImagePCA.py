from PIL import Image
import numpy as np
import scipy.sparse.linalg as splg
import os



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

    Catatan:
    - Pastikan library sudah terinstall
    - X_mean_array adalah mean dari setiap pixel yang di-precompute pada tahap preprocessing
    - U adalah matrix dari k principal components yang dihitung dari SVD
    """
    
    def __init__(self):
        self.U = None
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
        len_image = len(images_array_1d[0])
        std_images = []

        images_array_1d_np = np.array([img.astype(np.float32) for img in images_array_1d])
        
        # Pre-calculate mean of each pixel
        mean_array = np.mean(images_array_1d_np, axis=0)
        
        # Standardize each pixel
        for i in range(N):
            std_image = np.zeros(len_image, dtype=np.float32)
            for j in range(len_image):
                std_image[j] = ImagePCA.standardizePixel(images_array_1d[i][j], mean_array[j])
            std_images.append(np.array(std_image, dtype=np.float32))
        
        return (std_images, mean_array)
            
    @staticmethod
    def preprocessImage(image, width, height):
        """
        Preprocesses the image by converting it to numpy array
        """
        image_resized = image.resize((width, height), Image.BICUBIC)
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
        images_preprocessed = []
        for img in images:
            img_prep = ImagePCA.preprocessImage(img, width, height)
            images_preprocessed.append(img_prep)
        std_images, mean_array = ImagePCA.stadardizeGrayImages(images_preprocessed)
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
    def svdKPrincipleComponents(X, k_components):
        """
        Returns:
        U_k, S_k, Vt_k
        """
        U_k, S_k, Vt_k = splg.svds(X, k_components, which='LM', return_singular_vectors="u")
        return U_k, S_k, Vt_k
    
    def fit(self, images, mean_array, k_components=50):
        """
        Fits the PCA model to the images
        Args:
        images: List of images as numpy arrays
        n_components: Number of components to keep
        """
        X = ImagePCA.imagesListToArray(images)        
        cov = ImagePCA.covariance(X)
        
        U, S, Vt = ImagePCA.svdKPrincipleComponents(cov, k_components)
        idx = np.argsort(S)[::-1]   # Indices to sort singular values in descending order
        S = S[idx]                  # Sorted singular values
        U = U[:, idx]               # Reorder left singular vectors
        self.U = U
        self.X_mean_array = mean_array
        self.fit_done = True

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
        if not self.fit_done:
            raise ValueError('Fit the model first')
        
        query_Z = ImagePCA.projectToPrincipalComponents(prepocessed_query, self.U)
        
        distances = []
        for i, img in enumerate(preprocessed_images):
            img_Z = ImagePCA.projectToPrincipalComponents(img, self.U)
            distance = ImagePCA.euclideanDistance(query_Z, img_Z)
            distances.append((i, distance))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]