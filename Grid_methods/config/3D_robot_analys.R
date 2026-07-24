library(ggplot2)

setwd('/mnt/c9cf456b-9a69-4cb2-a7d6-4f9b7533bd83/Fitness_score/Fitness_score/data')

df = read.csv('3DRobot_table_25.csv')

# plot the fitness scorggplot(df_3NE0A, aes(x=name_decoy ,y=Fitness.Score, color=color))+
#   geom_point() +
#   geom_line() + ggtitle('Fitness score of 3NE0A') + xlab('Time') + ylab('Fitness score')+
#           theme_bw(base_size=4)+
#             theme(axis.text.x = element_text(angle = 90, hjust = 1))+
#   ylim(min(df_3NE0A$Fitness.Score)-0.005, max(df_3NE0A$Fitness.Score)+0.005)e when Protein_name is '3NE0A'
l_protein = unique(df$Protein_name)
#loop over the protein names
for (protein in l_protein){
  df_protein = df[df$Protein_name == protein,]
  # add a colum color with red when name_decoy is 'native_wat'
  df_protein$color = ifelse(df_protein$name_decoy == 'Native', 'red', 'black')
  #plot the fitness score
  p = ggplot(df_protein, aes(x=RMSD ,y=Fitness.Score, color=color))+
    geom_point() +
    geom_line() +
    ggtitle(paste('Fitness score of', protein)) + xlab('RMSD') + ylab('Fitness score')+
    xlim(min(df_protein$RMSD)-0.05, max(df_protein$RMSD)+0.05)+
    theme_bw(base_size=4)+
    theme(axis.text.x = element_text(angle = 90, hjust = 1))+
    ylim(0, 1)
  #save the plot
  ggsave(paste('./plot_rmsd_score_01/Fitness_score_', protein, '.png', sep=''))
}

df_3NE0A = df[df$Protein_name == '1FX2A',]
# add a colum color with red when name_decoy is 'native_wat'
df_3NE0A$color = ifelse(df_3NE0A$name_decoy == 'Native', 'red', 'black')





#color the points in red when name_decoy is 'native_wat'

ggplot(df_3NE0A, aes(x=RMSD ,y=Fitness.Score, color=color))+
  geom_point() +
  geom_line() +
  ggtitle('Fitness score of 3NE0A') + xlab('RMSD') + ylab('Fitness score')+
  xlim(min(df_3NE0A$RMSD)-0.05, max(df_3NE0A$RMSD)+0.05)+
    theme_bw(base_size=4)+
    theme(axis.text.x = element_text(angle = 90, hjust = 1))+
    ylim(min(df_3NE0A$Fitness.Score)-0.005, max(df_3NE0A$Fitness.Score)+0.005)

