library(ggplot2)
library(viridis)

# categories ===========================================

topics <- read.csv("tidy.csv")
topics$topic <- factor(topics$topic, levels=c("quran", "hadith", "faiths/beliefs", "prayers/duties", "family/women", "financial issues", "society/politics"), labels=c("Quran", "Hadith", "Faiths / beliefs", "Prayers / duties", "Family / women", "Financial issues", "Society / politics"))

ggplot(topics, aes(x=topic, y=n)) +
    geom_bar(stat="identity", fill="#35b779") +
    labs(x="Topic",
         y="Frequency",
         title="Number of posts by category") +
    theme(axis.text.x = element_text(angle = 35, hjust = 1),
          plot.background = element_rect(fill = "transparent",color = NA))
ggsave("../plots/category-totals.pdf", width=8, height=5, family="Times")


ggplot(topics, aes(x=site, y=n, fill=topic)) +
    geom_bar(stat="identity", position="stack") +
    labs(x="Website",
         y="Frequency",
         fill="Topic",
         title="Number of posts in each category by site") +
    scale_fill_viridis_d() +
    theme(axis.text.x = element_text(angle = 35, hjust = 1),
          plot.background = element_rect(fill = "transparent",color = NA),
          legend.background = element_rect(fill = "transparent",color = NA))
ggsave("../plots/by-site-frequency.pdf", width=8, height=5, family="Times")

ggplot(topics, aes(x=site, y=n, fill=topic,)) +
    geom_bar(stat="identity", position="fill") +
    scale_fill_viridis_d() +
    labs(x="Website",
         y="Proportion of posts",
         title="Distribution of post cateogires for each site",
         fill="Topic") +
    theme(axis.text.x = element_text(angle = 35, hjust = 1),
          plot.background = element_rect(fill = "transparent",color = NA),
          legend.background = element_rect(fill = "transparent",color = NA))
ggsave("../plots/by-site-density.pdf", width=8, height=5, family="Times")




# tfidf ===========================================

tfidf <- read.csv("tfidf-by-site.csv", stringsAsFactors=TRUE)

tfidf <- tfidf %>% rename(mean_tfidf=tfidf,
                          website=category)

labels <- c(aboutislam="About Islam", darulifta="Darul Iifta Deoband", eshaykh="eShaykh.com", islamqa="Islam Q&A", islamweb="islamweb.net", sistani="sistani.org")

tfidf <- transform(tfidf, feature2 = factor(paste(website, feature)))
## tfidf <- arrange(tfidf, feature2)
tfidf <- transform(tfidf, feature2 = reorder(feature2, rank(mean_tfidf)))

ggplot(tfidf, aes(x=feature2, y=mean_tfidf, fill=website)) +
    geom_bar(stat="identity") +
    ## geom_label(mapping=aes(y=0), fill="white") +
    facet_wrap(.~website, ncol=3, scales="free", labeller = labeller(website=labels)) +
    coord_flip() +
    scale_fill_viridis_d() +
    scale_x_discrete(labels=tfidf$feature, breaks=tfidf$feature2) +
    theme(axis.text.x = element_text(angle = 45, hjust=1),
          legend.position="none") +
    labs(x="Word / Bigram", y="Mean TF-IDF")
ggsave("../plots/tfidf.pdf", width = 7, height=9, family="Times", device=cairo_pdf)


# above from https://stackoverflow.com/questions/5409776/how-to-order-bars-in-faceted-ggplot2-bar-chart
## two_groups <- data.frame(
##     height   = runif(10),
##     category = gl(5, 2),
##     group    = gl(2, 1, 10, labels = letters[1:2])
## )

## two_groups <- transform(two_groups, category2 = factor(paste(group, category)))
## two_groups <- transform(two_groups, category2 = reorder(category2, rank(height)))

## ggplot(two_groups, aes(category2, height)) +
##     geom_bar(stat = "identity") +
##     facet_grid(. ~ group, scales = "free_x") +
##     scale_x_discrete(labels=two_groups$category, breaks=two_groups$category2)
