#!/usr/bin/env nextflow

nextflow.enable.dsl=2


def helpMessage() {
	log.info """
	BLAH!	
	""".stripIndent()
}

if (params.help) {
	helpMessage()
	exit 0
} else {
	params.help = ""
}

if (params.rna) {
	params.strand_specific = "--strand_specific"
} else {
	params.strand_specific = ""
}

if (!params.ambig_mode) {
	params.ambig_mode = "unique_only"
}

if (!params.mode) {
	params.mode = "genome"
}

if (!params.db) {
	if (params.mode == "genome") {
		params.db = "${params.genome_db}"
	} else if (params.mode == "genes") {
		params.db = "${params.genes_db}"
	} else if (params.mode == "domain") {
		params.db = "${params.domain_db}"
	}
}

if (!params.file_pattern) {
	params.file_pattern = "**.bam"
}

if (!params.publish_mode) {
	params.publish_mode = "link"
}

if (!params.output_dir) {
	params.output_dir = "gffquant_out"
}
output_dir = "${params.output_dir}/${params.ambig_mode}_${params.mode}"

suffix_pattern = params.file_pattern.replaceAll(/\*\*/, "")


process run_gffquant {
	publishDir "${output_dir}", mode: params.publish_mode

	input:
	tuple val(sample), path(bam)
	path(db)

	output:
	tuple val(sample), path("${sample}/*.txt.gz"), emit: results

	script:
	def gq_params = "-o ${sample}/${sample} -m ${params.mode} --ambig_mode ${params.ambig_mode} ${params.strand_specific}"
	if (params.do_name_sort) {
		"""
		mkdir -p logs/
		samtools collate -O ${bam} -@ ${task.cpus} | gffquant ${gq_params} ${db} - > logs/${sample}.o 2> logs/${sample}.e
		"""
	} else {
		"""
		mkdir -p logs/
		gffquant ${gq_params} ${db} ${bam} > logs/${sample}.o 2> logs/${sample}.e
		"""
	}
}

process collate_feature_counts {
	publishDir "${output_dir}", mode: params.publish_mode

	input:
	tuple val(sample), path(count_tables)

	output:
	path("collated/*.txt.gz"), emit: collated, optional: true

	script:
	"""
	mkdir -p collated/
	collate_counts . -o collated/collated -c uniq_scaled
	collate_counts . -o collated/collated -c combined_scaled
	"""
}


workflow {

	bam_ch = Channel
		.fromPath(params.input_dir + "/" + params.file_pattern)
		.map { file ->
			def sample = file.name.replaceAll(suffix_pattern, "")
			sample = sample.replaceAll(/\.$/, "")
			return tuple(sample, file)
		}
		.groupTuple(sort:true)

	run_gffquant(bam_ch, params.db)

	feature_count_ch = run_gffquant.out.results //.collect()
		.map { sample, files -> return files }
		.flatten()
		.filter { !it.name.endsWith("gene_counts.txt") }
		.filter { !it.name.endsWith("seqname.uniq.txt") }
		.filter { !it.name.endsWith("seqname.dist1.txt") }
		.map { file -> 
			def category = file.name.replaceAll(/\.txt$/, "")
				.replaceAll(/.+\./, "")
			return tuple(category, file)
		}
		.groupTuple(sort:true)

	//feature_count_ch.view()

	if (!params.no_collate) {

		collate_feature_counts(feature_count_ch)

	}

}
