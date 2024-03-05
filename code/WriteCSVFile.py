import csv
import sys
import os
## Choose a gene from "gencode.v26.GRCh38.genes.mapped.no_sex.csv"
## gencode.v26.GRCh38.genes.mapped.no_sex.csv contains: CHR,START,END,GENE_ID
## We next characterized each gene potentially regulated by all possible susceptible TFs based on the evidence of their TF-DNA binding sites that are located in its flanking 20Kb of TSS
select_gene_id = sys.argv[1]

tss_file=open("/PATH_TO/TSS_Region_Estimate_Breast_Tissue.txt",'r')
for line in tss_file:
    curr_geneid=line.split("\t")[0].strip()
    if curr_geneid == select_gene_id:
        target_chr=line.split("\t")[2].strip()
        curr_tss=int(line.split("\t")[4].strip())
        loc_start=curr_tss-20000
        loc_end=curr_tss+20000
tss_file.close()


TF_snp_matchID_file = "/PATH_TO/BC_SNP_TFbindings_Select_weight_stratify_b38.tped_chr"+target_chr+".txt" # Functional variants
sel_tf_name=[]
with open(TF_snp_matchID_file) as tf_snp_txt:
    readTFtxt = csv.reader(tf_snp_txt, delimiter='\t')
    header = next(readTFtxt) ##only read the header
    for row in readTFtxt:
        curr_tmp_chr = row[2].strip()
        if curr_tmp_chr == target_chr:
            curr_tmp_loc = row[3].strip()
            if loc_start <= int(curr_tmp_loc) <=loc_end:
                for curr_tf_idx in row[8:]:
                    if curr_tf_idx not in sel_tf_name:
                        sel_tf_name.append(curr_tf_idx)

tf_snp_txt.close()
print(sel_tf_name)

sel_snp_tf=open("/PATH_TO/TFs_Trans_Variants_All_2k.txt",'r')
lines=sel_snp_tf.readlines()
sel_b38_dict={}
for line in lines[1:]:
    if line.split("\t")[1].strip() in sel_tf_name:
        if line.split("\t")[1].strip() not in sel_b38_dict.keys():
            sel_b38_dict[line.split("\t")[1].strip()]={}
        for curr_b38 in line.split("\t")[3:]:
            curr_chr=curr_b38.split("_")[0].strip().split("chr")[1].strip()
            if curr_chr not in sel_b38_dict[line.split("\t")[1].strip()].keys():
                sel_b38_dict[line.split("\t")[1].strip()][curr_chr]=[]
            sel_b38_dict[line.split("\t")[1].strip()][curr_chr].append(curr_b38.strip())
sel_snp_tf.close()

working_dir="/PATH/TO/DIR/"
if len(sel_b38_dict.keys()) !=0:
    if not os.path.exists(working_dir+select_gene_id):
        os.makedirs(working_dir+select_gene_id)
    outtxtFile = open(working_dir+select_gene_id+"/"+select_gene_id+".TF2TF_sel_trans.txt", "w")
    outtxtFile.write("TF\tvar_name_b38\tvar_name_b37\tchr_b38\tposition_b38\ta0\trs\tbeta\tbeta_stratify\tTF_binding")
    for curr_tf in sel_b38_dict.keys():
        index=0
        for curr_chr in sel_b38_dict[curr_tf]:
            in_tfe_file=open("/PATH_TO/TF_Combine_All_Function_chr"+str(curr_chr)+".txt",'r')
            for line in in_tfe_file:
                curr_b38="chr"+line.split("\t")[0].strip()+"_b38"
                tf_index=curr_tf+"_"+str(index)
                if curr_b38 in sel_b38_dict[curr_tf][curr_chr]:
                    outtxtFile.write("\n"+tf_index+"\t"+line.strip())
                    index+=1
    outtxtFile.close()

tf_file=open("./Gene_ID/"+select_gene_id+"/"+select_gene_id+".TF2TF_sel_trans.txt",'r')
sel_chr_b38={}
b38_tf_dict={}
tf_lines=tf_file.readlines()
for line in tf_lines[1:]:
    curr_tf=line.split("\t")[0].strip()
    if line.split("\t")[3].strip() == target_chr:
        if target_chr not in sel_chr_b38.keys():
            sel_chr_b38[target_chr] = []
        tmp_pos=int(line.split("\t")[4].strip())
        curr_b38="chr"+line.split("\t")[1].strip()+"_b38"
        if (tmp_pos < loc_start) or (tmp_pos>loc_end):
            if (curr_b38 not in sel_chr_b38[target_chr]):
                sel_chr_b38[target_chr].append(curr_b38)
                b38_tf_dict[curr_b38]=curr_tf
    if line.split("\t")[3].strip() != target_chr:
        if line.split("\t")[3].strip() not in sel_chr_b38.keys():
            sel_chr_b38[line.split("\t")[3].strip()] = []
        curr_b38="chr"+line.split("\t")[1].strip()+"_b38"
        if (curr_b38 not in sel_chr_b38[line.split("\t")[3].strip()]):
                sel_chr_b38[line.split("\t")[3].strip()].append(curr_b38)
                b38_tf_dict[curr_b38]=curr_tf
tf_file.close()
    
 ## First read GTEx genotype file,and start to write new csv file for the select_gene_id
outcsvFile = open("./Gene_ID/"+select_gene_id+"/"+select_gene_id+".TF2TF_sel_trans.csv", "w")
gtex_matchID_file = "/PATH_TO/GTEx_maf0.01/Breast_Female/GTEx_v8_866Indiv_maf0.01_breast_female_tped_chr"+target_chr+".num.overlap.csv"
with open(gtex_matchID_file) as gtex_genotype_csv:
    readgtexCSV = csv.reader(gtex_genotype_csv, delimiter=',')
    gtex_header = next(readgtexCSV) ##only read the header
    outcsvFile.write("TF,"+gtex_header[0].strip()+","+gtex_header[1].strip()+","+gtex_header[2].strip())
    for curr_id in gtex_header[3:]:
        outcsvFile.write(","+curr_id.strip())
gtex_genotype_csv.close()
