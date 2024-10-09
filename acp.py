#Creer par Mohamed


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.spatial import ConvexHull
import matplotlib as mpl
import matplotlib.cm as cm
import seaborn as sns

# Load the dataset from a CSV file
dfBook = pd.read_csv("bigboss_book.csv", low_memory=False)

# Select quantitative data columns for analysis
quantitativesDataBook = dfBook[["rating_count", "review_count", "average_rating", "five_star_ratings", 
                                  "four_star_ratings", "three_star_ratings", "two_star_ratings", 
                                  "one_star_ratings", "number_of_pages", "year_published"]]

# Remove rows with missing values to ensure clean data
quantitativesDataBook = quantitativesDataBook.dropna()

# Standardize the data to have a mean of 0 and a standard deviation of 1
X = StandardScaler().fit_transform(quantitativesDataBook)

# Perform PCA with 2 components
pca = PCA(n_components=2)
pca.fit(X)  # Fit the PCA model on the standardized data
pca_res = pca.transform(X)  # Transform the data to the PCA space

# Calculate explained variance for each principal component
y1 = list(pca.explained_variance_ratio_)  # Variance explained by each principal component

# Function to create a biplot for visualizing PCA results
def biplot(pca=[], x=None, y=None, components=[0, 1], score=None, coeff=None, 
           coeff_labels=None, score_labels=None, circle='T', bigdata=1000, cat=None, 
           cmap="viridis", density=True):

    if isinstance(pca, PCA):
        coeff = np.transpose(pca.components_[components, :])
        score = pca.fit_transform(x)[:, components]

        if isinstance(x, pd.DataFrame):
            coeff_labels = list(x.columns)

    if score is not None:
        x = score

    if x.shape[1] > 1:
        xs = x[:, 0]
        ys = x[:, 1]
    else:
        xs = x
        ys = y

    if len(xs) != len(ys):
        print("Warning! x and y do not have the same length!")

    scalex = 1.0 / (xs.max() - xs.min())
    scaley = 1.0 / (ys.max() - ys.min())

    temp = (xs - xs.min())
    x_c = temp / temp.max() * 2 - 1

    temp = (ys - ys.min())
    y_c = temp / temp.max() * 2 - 1

    data = pd.DataFrame({"x_c": x_c, "y_c": y_c})
    print("Note: Data has been centered and scaled for visualization.")

    if cat is None:
        cat = [0] * len(xs)
    elif len(pd.Series(cat)) == 1:
        cat = list(pd.Series(cat)) * len(xs)
    elif len(pd.Series(cat)) != len(xs):
        print("Warning! Anomalous number of categories!")

    cat = pd.Series(cat).astype("category")

    fig = plt.figure(figsize=(6, 6), facecolor='w')
    ax = fig.add_subplot(111)

    if len(xs) < bigdata:
        ax.scatter(x_c, y_c, c=cat.cat.codes, cmap=cmap)

        if density:
            print("Warning! Density mode only appears if BigData is set.")

    else:
        norm = mpl.colors.Normalize(vmin=0, vmax=(len(np.unique(cat.cat.codes))))
        cmap = cmap
        m = cm.ScalarMappable(norm=norm, cmap=cmap)

        if density:
            sns.set_style("white")
            sns.kdeplot(x="x_c", y="y_c", data=data)

            if len(np.unique(cat)) <= 1:
                sns.kdeplot(x="x_c", y="y_c", data=data, cmap="Blues", shade=True, thresh=0)
            else:
                for i in np.unique(cat):
                    color_temp = m.to_rgba(i)
                    sns.kdeplot(x="x_c", y="y_c", data=data[cat == i], color=color_temp,
                                shade=True, thresh=0.25, alpha=0.25)

        for cat_temp in cat.cat.codes.unique():
            x_c_temp = [x_c[i] for i in range(len(x_c)) if (cat.cat.codes[i] == cat_temp)]
            y_c_temp = [y_c[i] for i in range(len(y_c)) if (cat.cat.codes[i] == cat_temp)]

            points = np.array([x_c_temp, y_c_temp]).T
            hull = ConvexHull(points)

            for simplex in hull.simplices:
                color_temp = m.to_rgba(cat_temp)
                plt.plot(points[simplex, 0], points[simplex, 1], color=color_temp)

    if coeff is not None:
        if circle == 'T':
            x_circle = np.linspace(-1, 1, 100)
            y_circle = np.linspace(-1, 1, 100)
            X, Y = np.meshgrid(x_circle, y_circle)
            F = X ** 2 + Y ** 2 - 1.0
            plt.contour(X, Y, F, [0])

        n = coeff.shape[0]
        for i in range(n):
            plt.arrow(0, 0, coeff[i, 0], coeff[i, 1], color='r', alpha=0.5,
                      head_width=0.05, head_length=0.05)
            if coeff_labels is None:
                plt.text(coeff[i, 0] * 1.15, coeff[i, 1] * 1.15, "Var" + str(i + 1), color='g', ha='center', va='center')
            else:
                plt.text(coeff[i, 0] * 1.15, coeff[i, 1] * 1.15, coeff_labels[i], color='g', ha='center', va='center')

    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    plt.xlabel("PC{}".format(1))
    plt.ylabel("PC{}".format(2))
    plt.grid(linestyle='--')
    plt.show()

# Use the biplot function to visualize PCA results
biplot(score=pca_res[:, 0:2],  # Use the first two PCA scores
       coeff=np.transpose(pca.components_[0:2, :]),  # Coefficients for the first two components
       coeff_labels=quantitativesDataBook.columns,  # Labels for the coefficients
       cat=y1[0:1],  # Categories for coloring (explained variance in this case)
       density=False)  # Disable density mode
