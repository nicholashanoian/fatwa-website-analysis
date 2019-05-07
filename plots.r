library(ggplot2)
library(viridis)


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

